from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "toolchain.py"
SPEC = importlib.util.spec_from_file_location("pleiades_toolchain", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def one_tool_catalog() -> dict:
    return {
        "schema": MODULE.CATALOG_SCHEMA,
        "policy": {"default_profile": "core"},
        "tools": [
            {
                "name": "one",
                "url": "https://github.com/example/project.git",
                "category": "test",
                "profiles": ["core"],
                "ref": None,
                "license_hint": "MIT",
                "license_review": "required",
            }
        ],
    }


def valid_lock(catalog: dict) -> dict:
    return {
        "schema": MODULE.LOCK_SCHEMA,
        "catalog_schema": MODULE.CATALOG_SCHEMA,
        "catalog_sha256": MODULE.canonical_sha256(catalog),
        "selection": {"profiles": ["core"], "tools": []},
        "tools": {
            "one": {
                "commit": "a" * 40,
                "url": "https://github.com/example/project.git",
                "ref": "HEAD",
            }
        },
    }


def lock_args(catalog: pathlib.Path, lock: pathlib.Path, *, keep_going: bool):
    return argparse.Namespace(
        catalog=catalog,
        lock=lock,
        profile=[],
        tool=[],
        keep_going=keep_going,
    )


def git(*arguments: str, cwd: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def initialized_repo(path: pathlib.Path) -> str:
    path.mkdir(parents=True)
    git("init", "--quiet", cwd=path)
    git("config", "user.email", "test@example.invalid", cwd=path)
    git("config", "user.name", "Factory Test", cwd=path)
    (path / "tracked.txt").write_text("original\n", encoding="utf-8")
    git("add", "tracked.txt", cwd=path)
    git("commit", "--quiet", "-m", "initial", cwd=path)
    git(
        "remote",
        "add",
        "origin",
        "https://github.com/example/project.git",
        cwd=path,
    )
    return git("rev-parse", "HEAD", cwd=path)


class ToolchainTests(unittest.TestCase):
    def test_repository_catalog_is_valid(self) -> None:
        catalog = MODULE.load_json(ROOT / "catalog" / "tools.catalog.json")
        tools = MODULE.validate_catalog(catalog)
        self.assertGreater(len(tools), 10)
        self.assertEqual(len(tools), len({tool["name"] for tool in tools}))

    def test_core_profile_is_bounded(self) -> None:
        catalog = MODULE.load_json(ROOT / "catalog" / "tools.catalog.json")
        tools = MODULE.validate_catalog(catalog)
        selected = MODULE.select_tools(tools, ["core"], [])
        self.assertGreater(len(selected), 0)
        self.assertLess(len(selected), len(tools))
        self.assertTrue(all("core" in tool["profiles"] for tool in selected))

    def test_core_is_default_only_without_explicit_selection(self) -> None:
        self.assertEqual(MODULE.resolve_selection([], []), (["core"], []))
        self.assertEqual(MODULE.resolve_selection(["memory"], []), (["memory"], []))
        self.assertEqual(MODULE.resolve_selection([], ["repomix"]), ([], ["repomix"]))

    def test_explicit_profile_does_not_append_core(self) -> None:
        catalog = MODULE.load_json(ROOT / "catalog" / "tools.catalog.json")
        tools = MODULE.validate_catalog(catalog)
        profiles, names = MODULE.resolve_selection(["memory"], [])
        selected = MODULE.select_tools(tools, profiles, names)
        self.assertTrue(all("memory" in tool["profiles"] for tool in selected))

    def test_explicit_tool_does_not_append_core(self) -> None:
        catalog = MODULE.load_json(ROOT / "catalog" / "tools.catalog.json")
        tools = MODULE.validate_catalog(catalog)
        profiles, names = MODULE.resolve_selection([], ["repomix"])
        selected = MODULE.select_tools(tools, profiles, names)
        self.assertEqual([tool["name"] for tool in selected], ["repomix"])

    def test_unknown_tool_fails(self) -> None:
        catalog = MODULE.load_json(ROOT / "catalog" / "tools.catalog.json")
        tools = MODULE.validate_catalog(catalog)
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.select_tools(tools, [], ["does-not-exist"])

    def test_duplicate_url_fails(self) -> None:
        catalog = one_tool_catalog()
        duplicate = dict(catalog["tools"][0])
        duplicate["name"] = "two"
        duplicate["url"] = "https://github.com/example/project"
        catalog["tools"].append(duplicate)
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_catalog(catalog)

    def test_option_like_or_whitespace_ref_fails(self) -> None:
        for bad_ref in ("--upload-pack=evil", "feature branch", "line\nbreak"):
            catalog = one_tool_catalog()
            catalog["tools"][0]["ref"] = bad_ref
            with self.assertRaises(MODULE.ToolchainError):
                MODULE.validate_catalog(catalog)

    def test_valid_lock_is_bound_to_catalog_url_ref_and_selection(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        self.assertEqual(
            MODULE.validate_lock(valid_lock(catalog), catalog, tools),
            {"one": "a" * 40},
        )

    def test_lock_requires_exact_lowercase_commit(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        lock = valid_lock(catalog)
        lock["tools"]["one"]["commit"] = "main"
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_lock(lock, catalog, tools)

    def test_lock_rejects_catalog_drift(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        lock = valid_lock(catalog)
        catalog["policy"]["default_profile"] = "changed"
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_lock(lock, catalog, tools)

    def test_lock_rejects_upstream_url_or_ref_drift(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        lock = valid_lock(catalog)
        lock["tools"]["one"]["url"] = "https://github.com/example/other.git"
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_lock(lock, catalog, tools)
        lock = valid_lock(catalog)
        lock["tools"]["one"]["ref"] = "main"
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_lock(lock, catalog, tools)

    def test_lock_entries_must_match_recorded_selection(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        lock = valid_lock(catalog)
        lock["tools"] = {}
        with self.assertRaises(MODULE.ToolchainError):
            MODULE.validate_lock(lock, catalog, tools)

    def test_atomic_json_write_is_private_and_leaves_no_staging_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "state" / "value.json"
            MODULE.write_json_atomic(path, {"answer": 42})
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"answer": 42},
            )
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(path.parent.glob(f".{path.name}.tmp.*")), [])

    def test_failed_keep_going_preserves_existing_lock_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            catalog_path = root / "catalog.json"
            lock_path = root / "tools.lock.json"
            catalog_path.write_text(json.dumps(one_tool_catalog()), encoding="utf-8")
            original = b'{"reviewed":"lock"}\n'
            lock_path.write_bytes(original)
            with mock.patch.object(
                MODULE,
                "run",
                side_effect=MODULE.ToolchainError("upstream unavailable"),
            ):
                result = MODULE.command_lock(
                    lock_args(catalog_path, lock_path, keep_going=True)
                )
            self.assertEqual(result, 1)
            self.assertEqual(lock_path.read_bytes(), original)

    def test_failed_initial_lock_creates_no_canonical_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            catalog_path = root / "catalog.json"
            lock_path = root / "tools.lock.json"
            catalog_path.write_text(json.dumps(one_tool_catalog()), encoding="utf-8")
            with mock.patch.object(
                MODULE,
                "run",
                side_effect=MODULE.ToolchainError("upstream unavailable"),
            ):
                result = MODULE.command_lock(
                    lock_args(catalog_path, lock_path, keep_going=True)
                )
            self.assertEqual(result, 1)
            self.assertFalse(lock_path.exists())

    def test_successful_lock_is_complete_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            catalog_path = root / "catalog.json"
            lock_path = root / "tools.lock.json"
            catalog = one_tool_catalog()
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            with mock.patch.object(
                MODULE,
                "run",
                return_value=("a" * 40) + "\tHEAD",
            ):
                result = MODULE.command_lock(
                    lock_args(catalog_path, lock_path, keep_going=False)
                )
            self.assertEqual(result, 0)
            lock = MODULE.load_json(lock_path)
            self.assertEqual(
                MODULE.validate_lock(lock, catalog, MODULE.validate_catalog(catalog)),
                {"one": "a" * 40},
            )
            self.assertEqual(lock_path.stat().st_mode & 0o777, 0o600)

    def test_dirty_locked_checkout_is_explicitly_non_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tools_dir = pathlib.Path(directory) / "tools"
            repo = tools_dir / "one"
            commit = initialized_repo(repo)
            (repo / "tracked.txt").write_text("locally changed\n", encoding="utf-8")
            tool = one_tool_catalog()["tools"][0]
            result = MODULE.sync_one(
                tool,
                tools_dir,
                commit,
                floating=False,
                update=False,
                allow_dirty=True,
            )
            self.assertEqual(result["action"], "present-dirty")
            self.assertFalse(result["reproducible"])
            self.assertTrue(result["worktree"]["dirty"])
            self.assertIn("tracked.txt", result["worktree"]["changed_paths"])
            first_digest = result["worktree"]["worktree_sha256"]
            (repo / "tracked.txt").write_text("another local change\n", encoding="utf-8")
            second_digest = MODULE.worktree_identity(repo)["worktree_sha256"]
            self.assertNotEqual(first_digest, second_digest)

    def test_dirty_checkout_cannot_move_to_another_locked_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tools_dir = pathlib.Path(directory) / "tools"
            repo = tools_dir / "one"
            initialized_repo(repo)
            (repo / "tracked.txt").write_text("locally changed\n", encoding="utf-8")
            with self.assertRaises(MODULE.ToolchainError):
                MODULE.sync_one(
                    one_tool_catalog()["tools"][0],
                    tools_dir,
                    "b" * 40,
                    floating=False,
                    update=False,
                    allow_dirty=True,
                )

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_symlinked_tool_destination_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            tools_dir = root / "tools"
            tools_dir.mkdir()
            outside = root / "outside"
            outside.mkdir()
            os.symlink(outside, tools_dir / "one", target_is_directory=True)
            with self.assertRaises(MODULE.ToolchainError):
                MODULE.sync_one(
                    one_tool_catalog()["tools"][0],
                    tools_dir,
                    None,
                    floating=True,
                    update=False,
                    allow_dirty=False,
                )


if __name__ == "__main__":
    unittest.main()
