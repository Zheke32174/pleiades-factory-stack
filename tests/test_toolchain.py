from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest

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

    def test_valid_lock_is_bound_to_catalog_url_ref_and_selection(self) -> None:
        catalog = one_tool_catalog()
        tools = MODULE.validate_catalog(catalog)
        self.assertEqual(MODULE.validate_lock(valid_lock(catalog), catalog, tools), {"one": "a" * 40})

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

    def test_atomic_json_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "state" / "value.json"
            MODULE.write_json_atomic(path, {"answer": 42})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"answer": 42})
            self.assertFalse(path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
