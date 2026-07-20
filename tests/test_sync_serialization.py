from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "toolchain.py"
SPEC = importlib.util.spec_from_file_location("serialized_toolchain", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def catalog_fixture() -> dict:
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


def lock_fixture(catalog: dict) -> dict:
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


def sync_args(root: pathlib.Path) -> argparse.Namespace:
    catalog = catalog_fixture()
    catalog_path = root / "catalog.json"
    lock_path = root / "tools.lock.json"
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    lock_path.write_text(json.dumps(lock_fixture(catalog)), encoding="utf-8")
    return argparse.Namespace(
        catalog=catalog_path,
        lock=lock_path,
        profile=[],
        tool=[],
        keep_going=False,
        tools_dir=root / "tools",
        state=root / "state" / "tools-state.json",
        floating=False,
        update=False,
        allow_dirty=False,
    )


def clean_result() -> dict:
    return {
        "name": "one",
        "url": "https://github.com/example/project.git",
        "ref": "HEAD",
        "commit": "a" * 40,
        "action": "updated",
        "category": "test",
        "license_hint": "MIT",
        "license_review": "required",
        "reproducible": True,
        "worktree": {
            "dirty": False,
            "staged_count": 0,
            "unstaged_count": 0,
            "untracked_count": 0,
            "changed_paths": [],
            "worktree_sha256": "b" * 64,
        },
        "dependency_manifests": [],
        "top_level_git_tree_only": True,
    }


class SyncSerializationTests(unittest.TestCase):
    def test_guard_is_stable_and_outside_mutable_tools_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tools = pathlib.Path(directory) / "tools"
            first = MODULE.sync_guard_path(tools)
            second = MODULE.sync_guard_path(tools)
            self.assertEqual(first, second)
            self.assertEqual(first.parent, tools.parent.resolve())
            self.assertNotEqual(first.parent, tools)
            self.assertIn(".tools.sync.", first.name)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_symlinked_tools_directory_is_rejected_before_locking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            outside = root / "outside"
            outside.mkdir()
            tools = root / "tools"
            os.symlink(outside, tools, target_is_directory=True)
            with self.assertRaisesRegex(MODULE.ToolchainError, "must not be a symlink"):
                MODULE.sync_guard_path(tools)

    def test_sync_guard_spans_checkout_and_state_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            args = sync_args(root)
            active = {"value": False}
            observed_guards: list[pathlib.Path] = []
            result = clean_result()

            @contextlib.contextmanager
            def guarded(path: pathlib.Path):
                self.assertFalse(active["value"])
                active["value"] = True
                observed_guards.append(path)
                try:
                    yield
                finally:
                    active["value"] = False

            def fake_sync(*_args, **_kwargs):
                self.assertTrue(active["value"])
                return result

            def fake_verify(*_args, **_kwargs):
                self.assertTrue(active["value"])

            original_write = MODULE.write_json_atomic

            def guarded_write(path: pathlib.Path, value: dict):
                self.assertTrue(active["value"])
                original_write(path, value)

            with (
                mock.patch.object(MODULE, "file_lock", guarded),
                mock.patch.object(MODULE, "sync_one", side_effect=fake_sync),
                mock.patch.object(
                    MODULE,
                    "verify_checkout_generation",
                    side_effect=fake_verify,
                ),
                mock.patch.object(
                    MODULE,
                    "write_json_atomic",
                    side_effect=guarded_write,
                ),
            ):
                return_code = MODULE.command_sync(args)

            self.assertEqual(return_code, 0)
            self.assertFalse(active["value"])
            self.assertEqual(observed_guards, [MODULE.sync_guard_path(args.tools_dir)])
            state = json.loads(args.state.read_text(encoding="utf-8"))
            self.assertEqual(state["sync_guard"], str(observed_guards[0]))
            self.assertEqual(len(state["checkout_generation_sha256"]), 64)
            self.assertTrue(state["reproducible"])

    def test_checkout_change_prevents_false_state_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            args = sync_args(root)
            guard = MODULE.sync_guard_path(args.tools_dir)
            result = clean_result()
            with (
                mock.patch.object(MODULE, "sync_one", return_value=result),
                mock.patch.object(MODULE, "git_head", return_value="c" * 40),
                mock.patch.object(
                    MODULE,
                    "worktree_identity",
                    return_value=result["worktree"],
                ),
            ):
                with self.assertRaisesRegex(
                    MODULE.ToolchainError,
                    "checkout changed before aggregate state publication",
                ):
                    MODULE._command_sync_locked(args, guard)
            self.assertFalse(args.state.exists())

    def test_generation_digest_binds_exact_checkout_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            args = sync_args(root)
            first = clean_result()
            second = clean_result()
            second["worktree"] = dict(second["worktree"])
            second["worktree"]["worktree_sha256"] = "d" * 64

            def run_with(result: dict) -> str:
                with (
                    mock.patch.object(MODULE, "sync_one", return_value=result),
                    mock.patch.object(
                        MODULE,
                        "verify_checkout_generation",
                        return_value=None,
                    ),
                ):
                    MODULE._command_sync_locked(args, MODULE.sync_guard_path(args.tools_dir))
                return json.loads(args.state.read_text(encoding="utf-8"))[
                    "checkout_generation_sha256"
                ]

            self.assertNotEqual(run_with(first), run_with(second))


if __name__ == "__main__":
    unittest.main()
