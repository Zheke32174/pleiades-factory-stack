#!/usr/bin/env python3
"""Manifest-driven third-party source synchronization for Pleiades Factory Stack."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import tempfile
from typing import Any

CATALOG_SCHEMA = "pleiades.factory-tool-catalog/v1"
LOCK_SCHEMA = "pleiades.factory-tool-lock/v1"
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


def normalize_url(url: str) -> str:
    value = url.strip().removesuffix("/").removesuffix(".git")
    return value.lower()


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
        normalized_url = normalize_url(url)
        if normalized_url in seen_urls:
            raise ToolchainError(f"duplicate tool URL: {url}")
        seen_urls.add(normalized_url)

        if not isinstance(category, str) or not NAME_RE.fullmatch(category):
            raise ToolchainError(f"{name}: invalid category")
        if not isinstance(profiles, list) or not profiles or not all(isinstance(p, str) and NAME_RE.fullmatch(p) for p in profiles):
            raise ToolchainError(f"{name}: profiles must be a non-empty list of safe names")
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


def validate_lock(lock: dict[str, Any], catalog_names: set[str]) -> dict[str, str]:
    if lock.get("schema") != LOCK_SCHEMA:
        raise ToolchainError(f"lock schema must be {LOCK_SCHEMA}")
    entries = lock.get("tools")
    if not isinstance(entries, dict):
        raise ToolchainError("lock tools must be an object")
    result: dict[str, str] = {}
    for name, value in entries.items():
        if name not in catalog_names:
            raise ToolchainError(f"lock contains unknown tool: {name}")
        if not isinstance(value, dict) or not isinstance(value.get("commit"), str) or not SHA_RE.fullmatch(value["commit"]):
            raise ToolchainError(f"lock entry for {name} must contain a lowercase 40-character commit SHA")
        result[name] = value["commit"]
    return result


def resolve_selection(profiles: list[str], names: list[str]) -> tuple[list[str], list[str]]:
    """Apply the core default only when the caller made no explicit selection."""
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
        validate_lock(load_json(args.lock), {tool["name"] for tool in tools})
    print(f"VALID catalog_tools={len(tools)} lock={'present' if args.lock.exists() else 'absent'}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    for tool in selected:
        status = "disabled-explicit" if not tool["enabled"] else "enabled"
        print(f"{tool['name']}\t{tool['category']}\t{status}\t{tool['url']}")
    print(f"selected={len(selected)}")
    return 0


def command_lock(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    entries: dict[str, dict[str, str]] = {}
    failures: list[str] = []
    for tool in selected:
        try:
            output = run(["git", "ls-remote", tool["url"], tool.get("ref") or "HEAD"], capture=True)
            first = output.splitlines()[0].split()[0] if output else ""
            if not SHA_RE.fullmatch(first):
                raise ToolchainError("upstream did not return a commit SHA")
            entries[tool["name"]] = {"commit": first, "url": tool["url"]}
            print(f"LOCK {tool['name']} {first}")
        except (ToolchainError, IndexError) as exc:
            failures.append(f"{tool['name']}: {exc}")
            if not args.keep_going:
                raise ToolchainError(failures[-1]) from exc
    lock = {
        "schema": LOCK_SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "catalog_schema": CATALOG_SCHEMA,
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
    if args.lock.exists():
        lock_entries = validate_lock(load_json(args.lock), {tool["name"] for tool in tools})

    missing = [tool["name"] for tool in selected if tool["name"] not in lock_entries]
    if missing and not args.floating:
        raise ToolchainError(
            "selected tools are not locked: " + ", ".join(missing) +
            "; run the lock command or pass --floating explicitly"
        )

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
        "schema": "pleiades.factory-tool-state/v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "tools_dir": str(args.tools_dir.resolve()),
        "profile": profiles,
        "tools": names,
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
