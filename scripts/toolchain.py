#!/usr/bin/env python3
"""Manifest-driven third-party source synchronization for Pleiades Factory Stack."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
import tempfile
import uuid
from typing import Any, Iterator

CATALOG_SCHEMA = "pleiades.factory-tool-catalog/v1"
LOCK_SCHEMA = "pleiades.factory-tool-lock/v2"
STATE_SCHEMA = "pleiades.factory-tool-state/v2"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DEPENDENCY_MANIFESTS = (
    ".gitmodules",
    "Cargo.lock",
    "Gemfile.lock",
    "go.sum",
    "package-lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "requirements.txt",
    "uv.lock",
    "yarn.lock",
)


class ToolchainError(RuntimeError):
    pass


def run(
    command: list[str],
    *,
    cwd: pathlib.Path | None = None,
    capture: bool = False,
) -> str:
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
        raise ToolchainError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{detail}"
        )
    return (result.stdout or "").strip()


def run_bytes(command: list[str], *, cwd: pathlib.Path) -> bytes:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ToolchainError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{detail}"
        )
    return result.stdout


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
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_url(url: str) -> str:
    return url.strip().removesuffix("/").removesuffix(".git").lower()


def safe_names(value: Any, field: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and NAME_RE.fullmatch(item) for item in value
    ):
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

        if (
            not isinstance(url, str)
            or not url.startswith("https://github.com/")
            or any(character.isspace() for character in url)
        ):
            raise ToolchainError(f"{name}: only HTTPS GitHub URLs are accepted")
        normalized = normalize_url(url)
        if normalized in seen_urls:
            raise ToolchainError(f"duplicate tool URL: {url}")
        seen_urls.add(normalized)

        if not isinstance(category, str) or not NAME_RE.fullmatch(category):
            raise ToolchainError(f"{name}: invalid category")
        safe_names(profiles, f"{name}.profiles", nonempty=True)
        if ref is not None and (
            not isinstance(ref, str)
            or not ref.strip()
            or ref.startswith("-")
            or any(character.isspace() or ord(character) < 32 for character in ref)
        ):
            raise ToolchainError(f"{name}: ref must be a bounded non-option string")
        if tool.get("license_review") not in {"required", "verified"}:
            raise ToolchainError(
                f"{name}: license_review must be required or verified"
            )
        if not isinstance(tool.get("license_hint"), str):
            raise ToolchainError(f"{name}: license_hint must be a string")
        tool.setdefault("enabled", True)
        if not isinstance(tool["enabled"], bool):
            raise ToolchainError(f"{name}: enabled must be boolean")
        validated.append(tool)
    return validated


def resolve_selection(
    profiles: list[str], names: list[str]
) -> tuple[list[str], list[str]]:
    if profiles or names:
        return list(profiles), list(names)
    return ["core"], []


def select_tools(
    tools: list[dict[str, Any]],
    profiles: list[str],
    names: list[str],
) -> list[dict[str, Any]]:
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
        raise ToolchainError(
            f"unknown tool name(s): {', '.join(sorted(missing))}"
        )
    if not selected:
        raise ToolchainError("selection is empty")
    return selected


def validate_lock(
    lock: dict[str, Any],
    catalog: dict[str, Any],
    tools: list[dict[str, Any]],
) -> dict[str, str]:
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
            raise ToolchainError(
                f"lock entry for {name} must contain a lowercase 40-character commit SHA"
            )
        if (
            not isinstance(value.get("url"), str)
            or normalize_url(value["url"]) != normalize_url(tool["url"])
        ):
            raise ToolchainError(
                f"lock entry for {name} is bound to a different upstream URL"
            )
        expected_ref = tool.get("ref") or "HEAD"
        if value.get("ref") != expected_ref:
            raise ToolchainError(
                f"lock entry for {name} was resolved from a different upstream ref"
            )
        result[name] = commit
    return result


def git_head(path: pathlib.Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=path, capture=True)


def decode_paths(raw: bytes, field: str) -> list[str]:
    result: list[str] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            result.append(item.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ToolchainError(f"{field} contains a non-UTF-8 path") from exc
    return result


def worktree_identity(path: pathlib.Path) -> dict[str, Any]:
    status_bytes = run_bytes(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=path,
    )
    diff_bytes = run_bytes(["git", "diff", "--binary", "HEAD", "--"], cwd=path)
    tracked_paths = decode_paths(
        run_bytes(["git", "diff", "--name-only", "-z", "HEAD", "--"], cwd=path),
        "changed tracked paths",
    )
    untracked_paths = decode_paths(
        run_bytes(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=path,
        ),
        "untracked paths",
    )

    staged = 0
    unstaged = 0
    untracked = 0
    for entry in status_bytes.split(b"\0"):
        if len(entry) < 3 or entry[2:3] != b" ":
            continue
        x = chr(entry[0])
        y = chr(entry[1])
        if x == "?" and y == "?":
            untracked += 1
            continue
        if x != " ":
            staged += 1
        if y != " ":
            unstaged += 1

    digest = hashlib.sha256()
    digest.update(b"porcelain-v1-z\0")
    digest.update(status_bytes)
    digest.update(b"\0diff-binary-head\0")
    digest.update(diff_bytes)
    for relative in sorted(untracked_paths):
        candidate = path / relative
        try:
            metadata = candidate.lstat()
        except OSError as exc:
            raise ToolchainError(
                f"cannot inspect untracked path {relative}: {exc}"
            ) from exc
        digest.update(b"\0untracked\0")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if stat.S_ISLNK(metadata.st_mode):
            digest.update(b"symlink\0")
            digest.update(os.readlink(candidate).encode("utf-8"))
        elif stat.S_ISREG(metadata.st_mode):
            digest.update(b"file\0")
            digest.update(candidate.read_bytes())
        else:
            digest.update(f"mode:{metadata.st_mode}".encode("ascii"))

    changed_paths = sorted(set(tracked_paths + untracked_paths))
    return {
        "dirty": bool(status_bytes),
        "staged_count": staged,
        "unstaged_count": unstaged,
        "untracked_count": untracked,
        "changed_paths": changed_paths,
        "worktree_sha256": digest.hexdigest(),
    }


def ensure_origin(path: pathlib.Path, expected_url: str) -> None:
    actual = run(["git", "remote", "get-url", "origin"], cwd=path, capture=True)
    if normalize_url(actual) != normalize_url(expected_url):
        raise ToolchainError(
            f"{path.name}: origin mismatch; expected {expected_url}, found {actual}"
        )


def validate_tool_destination(
    destination: pathlib.Path,
    name: str,
) -> pathlib.Path:
    if destination.exists() and destination.is_symlink():
        raise ToolchainError(f"tools directory must not be a symlink: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    base = destination.resolve()
    path = destination / name
    if path.is_symlink():
        raise ToolchainError(f"{name}: tool destination must not be a symlink")
    try:
        path.resolve(strict=False).relative_to(base)
    except ValueError as exc:
        raise ToolchainError(f"{name}: tool destination escapes tools_dir") from exc
    git_path = path / ".git"
    if git_path.is_symlink():
        raise ToolchainError(f"{name}: .git must not be a symlink")
    return path


def dependency_manifests(path: pathlib.Path) -> list[str]:
    return [name for name in DEPENDENCY_MANIFESTS if (path / name).is_file()]


def sync_one(
    tool: dict[str, Any],
    destination: pathlib.Path,
    commit: str | None,
    *,
    floating: bool,
    update: bool,
    allow_dirty: bool,
) -> dict[str, Any]:
    name = tool["name"]
    url = tool["url"]
    path = validate_tool_destination(destination, name)
    if path.exists() and not (path / ".git").is_dir():
        raise ToolchainError(
            f"{name}: destination exists but is not a Git repository: {path}"
        )

    action: str
    if path.exists():
        ensure_origin(path, url)
        before = worktree_identity(path)
        if before["dirty"] and not allow_dirty:
            raise ToolchainError(
                f"{name}: working tree is dirty; commit/stash changes or pass --allow-dirty"
            )
        if before["dirty"]:
            actual_before = git_head(path)
            if commit and actual_before != commit:
                raise ToolchainError(
                    f"{name}: dirty checkout is at {actual_before}, not locked commit {commit}; "
                    "refusing to move it"
                )
            if floating and update:
                raise ToolchainError(
                    f"{name}: refusing to update a dirty floating checkout"
                )
            action = "present-dirty"
        elif commit:
            run(["git", "fetch", "--depth=1", "origin", commit], cwd=path)
            run(["git", "checkout", "--detach", commit], cwd=path)
            action = "updated"
        elif floating and update:
            branch = run(
                [
                    "git",
                    "symbolic-ref",
                    "refs/remotes/origin/HEAD",
                    "--short",
                ],
                cwd=path,
                capture=True,
            )
            run(["git", "fetch", "--depth=1", "origin"], cwd=path)
            run(["git", "checkout", "--detach", branch], cwd=path)
            action = "updated"
        elif not commit and not floating:
            raise ToolchainError(f"{name}: no locked commit")
        else:
            action = "present"
    else:
        if commit:
            with tempfile.TemporaryDirectory(
                prefix=f"pleiades-{name}-",
                dir=destination,
            ) as temp_dir:
                temp = pathlib.Path(temp_dir)
                run(["git", "init", "--quiet", str(temp)])
                run(["git", "remote", "add", "origin", url], cwd=temp)
                run(["git", "fetch", "--depth=1", "origin", commit], cwd=temp)
                run(["git", "checkout", "--detach", commit], cwd=temp)
                temp.rename(path)
        elif floating:
            run(
                [
                    "git",
                    "clone",
                    "--filter=blob:none",
                    "--depth=1",
                    url,
                    str(path),
                ]
            )
        else:
            raise ToolchainError(
                f"{name}: no locked commit; create a lock or pass --floating"
            )
        action = "cloned"

    actual = git_head(path)
    if commit and actual != commit:
        raise ToolchainError(f"{name}: expected {commit}, checked out {actual}")
    worktree = worktree_identity(path)
    exact_locked_source = commit is not None and not worktree["dirty"]
    return {
        "name": name,
        "url": url,
        "ref": tool.get("ref") or "HEAD",
        "commit": actual,
        "action": action,
        "category": tool["category"],
        "license_hint": tool["license_hint"],
        "license_review": tool["license_review"],
        "reproducible": exact_locked_source,
        "worktree": worktree,
        "dependency_manifests": dependency_manifests(path),
        "top_level_git_tree_only": True,
    }


def write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            raise ToolchainError("durable JSON write made no progress")
        written += count


def fsync_directory(path: pathlib.Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


@contextlib.contextmanager
def file_lock(path: pathlib.Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def write_json_atomic(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    )
    data = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        write_all(fd, data)
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        temporary.unlink(missing_ok=True)
        raise
    else:
        os.close(fd)
    os.replace(temporary, path)
    os.chmod(path, 0o600)
    fsync_directory(path.parent)


def command_validate(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    if args.lock.exists():
        validate_lock(load_json(args.lock), catalog, tools)
    print(
        f"VALID catalog_tools={len(tools)} "
        f"catalog_sha256={canonical_sha256(catalog)} "
        f"lock={'present' if args.lock.exists() else 'absent'}"
    )
    return 0


def command_plan(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    for tool in selected:
        status = "disabled-explicit" if not tool["enabled"] else "enabled"
        print(
            f"{tool['name']}\t{tool['category']}\t{status}\t{tool['url']}"
        )
    print(f"selected={len(selected)} catalog_sha256={canonical_sha256(catalog)}")
    return 0


def command_lock(args: argparse.Namespace) -> int:
    catalog = load_json(args.catalog)
    tools = validate_catalog(catalog)
    profiles, names = resolve_selection(args.profile, args.tool)
    selected = select_tools(tools, profiles, names)
    guard = args.lock.with_name(f".{args.lock.name}.generation.lock")
    with file_lock(guard):
        entries: dict[str, dict[str, str]] = {}
        failures: list[str] = []
        for tool in selected:
            requested_ref = tool.get("ref") or "HEAD"
            try:
                output = run(
                    ["git", "ls-remote", tool["url"], requested_ref],
                    capture=True,
                )
                first = output.splitlines()[0].split()[0] if output else ""
                if not SHA_RE.fullmatch(first):
                    raise ToolchainError("upstream did not return a commit SHA")
                entries[tool["name"]] = {
                    "commit": first,
                    "url": tool["url"],
                    "ref": requested_ref,
                }
                print(f"LOCK {tool['name']} {first} {requested_ref}")
            except (ToolchainError, IndexError) as exc:
                failures.append(f"{tool['name']}: {exc}")
                if not args.keep_going:
                    raise ToolchainError(failures[-1]) from exc

        if failures:
            print(
                "lock failed; canonical lock was not replaced:",
                file=sys.stderr,
            )
            for failure in failures:
                print(f"  {failure}", file=sys.stderr)
            return 1

        lock = {
            "schema": LOCK_SCHEMA,
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "catalog_schema": CATALOG_SCHEMA,
            "catalog_sha256": canonical_sha256(catalog),
            "selection": {"profiles": profiles, "tools": names},
            "tools": entries,
        }
        validate_lock(lock, catalog, tools)
        write_json_atomic(args.lock, lock)
        print(f"lock_sha256={canonical_sha256(lock)} path={args.lock}")
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

    missing = [
        tool["name"] for tool in selected if tool["name"] not in lock_entries
    ]
    if missing and not args.floating:
        raise ToolchainError(
            "selected tools are not locked: "
            + ", ".join(missing)
            + "; run the lock command or pass --floating explicitly"
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

    reproducible = (
        not args.floating
        and not failures
        and bool(results)
        and all(result["reproducible"] for result in results)
    )
    state = {
        "schema": STATE_SCHEMA,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "catalog_sha256": canonical_sha256(catalog),
        "lock_sha256": lock_sha256,
        "tools_dir": str(args.tools_dir.resolve()),
        "selection": {"profiles": profiles, "tools": names},
        "floating": args.floating,
        "reproducible": reproducible,
        "source_scope": "top-level-git-tree-only",
        "results": results,
        "failures": failures,
    }
    write_json_atomic(args.state, state)
    print(
        f"summary: success={len(results)} failed={len(failures)} "
        f"reproducible={str(reproducible).lower()} state={args.state}"
    )
    return 1 if failures else 0


def build_parser(root: pathlib.Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        type=pathlib.Path,
        default=root / "catalog" / "tools.catalog.json",
    )
    parser.add_argument(
        "--lock",
        type=pathlib.Path,
        default=root / "catalog" / "tools.lock.json",
    )
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
            command.add_argument(
                "--state",
                type=pathlib.Path,
                default=root / "state" / "tools-state.json",
            )
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
