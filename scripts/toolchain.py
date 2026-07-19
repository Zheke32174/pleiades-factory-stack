#!/usr/bin/env python3
"""Manifest-driven third-party source synchronization for Pleiades Factory Stack."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Any

CATALOG_SCHEMA = "pleiades.factory-tool-catalog/v1"
LOCK_SCHEMA = "pleiades.factory-tool-lock/v2"
STATE_SCHEMA = "pleiades.factory-tool-state/v2"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ToolchainError(RuntimeError):
    pass


def run(command: list[str], *, cwd: pathlib.Path | None = None, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise ToolchainError(f"command failed ({result.returncode}): {' '.join(command)}\n{detail}")
    return (result.stdout or "").strip()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ToolchainError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ToolchainError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ToolchainError(f"JSON root must be an object: {path}")
    return value


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_url(url: str) -> str:
    return url.strip().removesuffix("/").removesuffix(".git").lower()


def safe_names(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and NAME_RE.fullmatch(item) for item in value):
        raise ToolchainError(f"{field} must be a list of safe names")
    if len(value) != len(set(value)):
        raise ToolchainError(f"{field} contains duplicates")
    if nonempty and not value:
        raise ToolchainError(f"{field} must not be empty")
    return list(value)


def validate_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ToolchainError(f"catalog schema must be {CATALOG_SCHEMA}")
    tools = catalog.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ToolchainError("catalog tools must be a non-empty list")

    seen_names: set[str] = set()
    seen_urls: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(tools):
        if not isinstance(raw, dict):
            raise ToolchainError(f"tools[{index}] must be an object")
        tool = dict(raw)
        name = tool.get("name")
        url = tool.get("url")
        category = tool.get("category")
        profiles = tool.get("profiles")
        ref = tool.get("ref")

        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            raise ToolchainError(f"tools[{index}].name is invalid")
        if name in seen_names:
            raise ToolchainError(f"duplicate tool name: {name}")
        seen_names.add(name)

        if not isinstance(url, str) or not url.startswith("https://github.com/") or any(c.isspace() for c in url):
            raise ToolchainError(f"{name}: only HTTPS GitHub URLs are accepted")
        normalized = normalize_url(url)
        if normalized in seen_urls:
            raise ToolchainError(f"duplicate tool URL: {url}")
        seen_urls.add(normalized)

        if not isinstance(category, str) or not NAME_RE.fullmatch(category):
            raise ToolchainError(f"{name}: invalid category")
        safe_names(profiles, f"{name}.profiles", nonempty=True)
        if ref is not None and (not isinstance(ref, str) or not ref.strip()):
            raise ToolchainError(f"{name}: ref must be null or a non-empty string")
        if tool.get("license_review") not in {"required", "verified"}:
            raise ToolchainError(f"{name}: license_review must be required or verified")
        if not isinstance(tool.get("license_hint"), str):
            raise ToolchainError(f"{name}: license_hint must be a string")
        tool.setdefault("enabled", True)
        if not isinstance(tool["enabled"], bool):
            raise ToolchainError(f"{name}: enabled must be boolean")
        validated.append(tool)
    return validated


def resolve_selection(profiles: list[str], names: list[str]) -> tuple[list[str], list[str]]:
    if profiles or names:
        return list(profiles), list(names)
    return ["core"], []


def select_tools(tools: list[dict[str, Any]], profiles: list[str], names: list[str]) -> list[dict[str, Any]]:
    requested_names = set(names)
    requested_profiles = set(profiles)
    selected = []
    for tool in tools:
        if not tool["enabled"] and tool["name"] not in requested_names:
            continue
        if requested_names and tool["name"] in requested_names:
            selected.append(tool)
        elif requested_profiles.intersection(tool["profiles"]):
            selected.append(tool)
    missing = requested_names.difference({tool["name"] for tool in tools})
    if missing:
        raise ToolchainError(f"unknown tool name(s): {', '.join(sorted(missing))}")
    if not selected:
        raise ToolchainError("selection is empty")
    return selected


def validate_lock(lock: dict[str, Any], catalog: dict[str, Any], tools: list[dict[str, Any]]) -> dict[str, str]:
    if lock.get("schema") != LOCK_SCHEMA:
        raise ToolchainError(f"lock schema must be {LOCK_SCHEMA}; regenerate the lock")
    if lock.get("catalog_schema") != CATALOG_SCHEMA:
        raise ToolchainError(f"lock catalog_schema must be {CATALOG_SCHEMA}")
    if lock.get("catalog_sha256") != canonical_sha256(catalog):
        raise ToolchainError("lock catalog_sha256 does not match the current catalog")

    selection = lock.get("selection")
    if not isinstance(selection, dict):
        raise ToolchainError("lock selection must be an object")
    profiles = safe_names(selection.get("profiles"), "lock selection.profiles")
    names = safe_names(selection.get("tools"), "lock selection.tools")
    if not profiles and not names:
        raise ToolchainError("lock selection must not be empty")

    entries = lock.get("tools")
    if not isinstance(entries, dict):
        raise ToolchainError("lock tools must be an object")
    catalog_by_name = {tool["name"]: tool for tool in tools}
    expected = {tool["name"] for tool in select_tools(tools, profiles, names)}
    if set(entries) != expected:
        raise ToolchainError("lock entries do not match the recorded selection")

    result: dict[str, str] = {}
    for name, value in entries.items():
        tool = catalog_by_name.get(name)
        if tool is None or not isinstance(value, dict):
            raise ToolchainError(f"invalid lock entry: {name}")
        commit = value.get("commit")
        if not isinstance(commit, str) or not SHA_RE.fullmatch(commit):
            raise ToolchainError(f"lock entry for {name} must contain a lowercase 40-character commit SHA")
        if not isinstance(value.get("url"), str) or normalize_url(value["url"]) != normalize_url(tool["url"]):
            raise ToolchainError(f"lock entry for {name} is bound to a different upstream URL")
        expected_ref = tool.get("ref") or "HEAD"
        if value.get("ref") != expected_ref:
            raise ToolchainError(f"lock entry for {name} was resolved from a different upstream ref")
        result[name] = commit
    return result


def git_head(path: pathlib.Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=path, capture=True)


def is_dirty(path: pathlib.Path) -> bool:
    return bool(run(["git", "status", "--porcelain"], cwd=path, capture=True))


def ensure_origin(path: pathlib.Path, expected_url: str) -> None:
    actual = run(["git", "remote", "get-url", "origin"], cwd=path, capture=True)
    if normalize_url(actual) != normalize_url(expected_url):
        raise ToolchainError(f"{path.name}: origin mismatch; expected {expected_url}, found {actual}")


def sync_one(tool: dict[str, Any], destination: pathlib.Path, commit: str | None, *, floating: bool, update: bool, allow_dirty: bool) -> dict[str, Any]:
    name = tool["name"]
    url = tool["url"]
    path = destination / name
    if path.exists() and not (path / ".git").is_dir():
        raise ToolchainError(f"{name}: destination exists but is not a Git repository: {path}")

    if path.exists():
        ensure_origin(path, url)
        if is_dirty(path) and not allow_dirty:
            raise ToolchainError(f"{name}: working tree is dirty; commit/stash changes or pass --allow-dirty")
        if commit:
            run(["git", "fetch", "--depth=1", "origin", commit], cwd=path)
            run(["git", "checkout", "--detach", commit], cwd=path)
        elif floating and update:
            branch = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD", "--short"], cwd=path, capture=True)
            run(["git", "fetch", "--depth=1", "origin"], cwd=path)
            run(["git", "checkout", "--detach", branch], cwd=path)
        elif not commit and not floating:
            raise ToolchainError(f"{name}: no locked commit")
        action = "updated" if commit or update else "present"
    else:
        if commit:
            destination.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=f"pleiades-{name}-", dir=destination) as temp_dir:
                temp = pathlib.Path(temp_dir)
                run(["git", "init", "--quiet", str(temp)])
                run(["git", "remote", "add", "origin", url], cwd=temp)
                run(["git", "fetch", "--depth=1", "origin", commit], cwd=temp)
                run(["git", "checkout", "--detach", commit], cwd=temp)
                temp.rename(path)
        elif floating:
            run(["git", "clone", "--filter=blob:none", "--depth=1", url, str(path)])
        else:
            raise ToolchainError(f"{name}: no locked commit; create a lock or pass --floating")
        action = "cloned"

    actual = git_head(path)
    if commit and actual != commit:
        raise ToolchainError(f"{name}: expected {commit}, checked out {actual}")
    return {
        "name": name,
        "url": url,
        "ref": tool.get("ref") or "HEAD",
        "commit": actual,
        "action": action,
        "category": tool["category"],
        "license_hint": tool["license_hint"],
        "license_review": tool["license_review"],
    }


def write_json_atomic(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def command_validate(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    if args.lock.exists():
        validate_lock(load_json(args.lock), catalog, tools)
    print(f"VALID catalog_tools={len(tools)} catalog_sha256={canonical_sha256(catalog)} lock={'present' if args.lock.exists() else 'absent'}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    for tool in selected:
        status = "disabled-explicit" if not tool["enabled"] else "enabled"
        print(f"{tool['name']}\t{tool['category']}\t{status}\t{tool['url']}")
    print(f"selected={len(selected)} catalog_sha256={canonical_sha256(catalog)}")
    return 0


def command_lock(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    entries: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for tool in selected:
        requested_ref = tool.get("ref") or "HEAD"
        try:
            output = run(["git", "ls-remote", tool["url"], requested_ref], capture=True)
            first = output.splitlines()[0].split()[0] if output else ""
            if not SHA_RE.fullmatch(first):
                raise ToolchainError("upstream did not return a commit SHA")
            entries[tool["name"]] = {"commit": first, "url": tool["url"], "ref": requested_ref}
            print(f"LOCK {tool['name']} {first} {requested_ref}")
        except (ToolchainError, IndexError) as exc:
            failures.append(f"{tool['name']}: {exc}")
            if not args.keep_going:
                raise ToolchainError(failures[-1]) from exc
    lock = {
        "schema": LOCK_SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "catalog_schema": CATALOG_SCHEMA,
        "catalog_sha256": canonical_sha256(catalog),
        "selection": {"profiles": profiles, "tools": names},
        "tools": entries,
    }
    write_json_atomic(args.lock, lock)
    if failures:
        print("lock completed with failures:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    return 0


def command_sync(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    lock_entries: dict[str, str] = {}
    lock_sha256: str | None = None
    if args.lock.exists():
        lock = load_json(args.lock)
        lock_entries = validate_lock(lock, catalog, tools)
        lock_sha256 = canonical_sha256(lock)

    missing = [tool["name"] for tool in selected if tool["name"] not in lock_entries]
    if missing and not args.floating:
        raise ToolchainError("selected tools are not locked: " + ", ".join(missing) + "; run the lock command or pass --floating explicitly")

    args.tools_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for tool in selected:
        try:
            result = sync_one(
                tool,
                args.tools_dir,
                lock_entries.get(tool["name"]),
                floating=args.floating,
                update=args.update,
                allow_dirty=args.allow_dirty,
            )
            results.append(result)
            print(f"{result['action'].upper()} {tool['name']} {result['commit']}")
        except ToolchainError as exc:
            failures.append({"name": tool["name"], "error": str(exc)})
            print(f"FAILED {tool['name']}: {exc}", file=sys.stderr)
            if not args.keep_going:
                break

    state = {
        "schema": STATE_SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "catalog_sha256": canonical_sha256(catalog),
        "lock_sha256": lock_sha256,
        "tools_dir": str(args.tools_dir.resolve()),
        "selection": {"profiles": profiles, "tools": names},
        "floating": args.floating,
        "results": results,
        "failures": failures,
    }
    write_json_atomic(args.state, state)
    print(f"summary: success={len(results)} failed={len(failures)} state={args.state}")
    return 1 if failures else 0


def build_parser(root: pathlib.Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=pathlib.Path, default=root / "catalog" / "tools.catalog.json")
    parser.add_argument("--lock", type=pathlib.Path, default=root / "catalog" / "tools.lock.json")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    for name in ("plan", "lock", "sync"):
        command = subparsers.add_parser(name)
        command.add_argument("--profile", action="append", default=[])
        command.add_argument("--tool", action="append", default=[])
        if name in {"lock", "sync"}:
            command.add_argument("--keep-going", action="store_true")
        if name == "sync":
            command.add_argument("--tools-dir", type=pathlib.Path, default=root / "tools")
            command.add_argument("--state", type=pathlib.Path, default=root / "state" / "tools-state.json")
            command.add_argument("--floating", action="store_true")
            command.add_argument("--update", action="store_true")
            command.add_argument("--allow-dirty", action="store_true")
    return parser


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    parser = build_parser(root)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            return command_validate(args)
        if args.command == "plan":
            return command_plan(args)
        if args.command == "lock":
            return command_lock(args)
        if args.command == "sync":
            return command_sync(args)
    except ToolchainError as exc:
        print(f"toolchain: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
