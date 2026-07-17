# Pleiades Factory Stack

A manifest-driven source catalog and synchronization layer for Pleiades research tools.

The repository does not treat “clone a pile of latest branches” as a reproducible toolchain. It separates:

- **catalog** — what projects are relevant and why;
- **lock** — the exact upstream commits selected for a reproducible checkout;
- **local state** — what is actually present under `tools/`;
- **integration** — a later, separately reviewed decision to build or expose a tool.

## Current status

Active research infrastructure, not a production package manager.

The current implementation:

- validates tool names, profiles, categories, HTTPS upstream URLs, and review metadata;
- supports small functional profiles instead of cloning every project by default;
- resolves exact upstream commit SHAs into a lock file;
- checks out pinned commits in detached HEAD state;
- rejects wrong-origin repositories and dirty trees by default;
- records actual checkout state and failures;
- never silently reports a failed clone as success;
- requires `--floating` before using an unpinned upstream head;
- clones source only—it does not build, execute, install, or grant capabilities;
- keeps Termux behavior in the separate Termux-specific repository.

## Layout

```text
catalog/tools.catalog.json     project inventory, profiles, URL, license-review state
catalog/tools.lock.json        generated exact commit pins; commit this after review
scripts/toolchain.py           validate, plan, lock, and sync engine
bootstrap-tools.sh             compatibility wrapper for `toolchain.py sync`
tools/                         local source checkouts; ignored
state/tools-state.json         actual checkout report; ignored
CREDITS.md                     attribution and license-review boundary
docs/                          research and integration notes
```

## Validate the catalog

```bash
python3 scripts/toolchain.py validate
```

## Inspect a profile

The default `core` profile is deliberately small.

```bash
python3 scripts/toolchain.py plan
python3 scripts/toolchain.py plan --profile memory
python3 scripts/toolchain.py plan --profile binary-analysis
python3 scripts/toolchain.py plan --profile all
```

A named tool can be selected directly:

```bash
python3 scripts/toolchain.py plan --tool repomix
```

## Create a reproducible lock

Resolve the current upstream heads for the selected profile:

```bash
python3 scripts/toolchain.py lock --profile core
```

Review and commit `catalog/tools.lock.json`. The lock records exact 40-character commit SHAs. Regenerating it is an explicit dependency update, not a side effect of routine startup.

Larger examples:

```bash
python3 scripts/toolchain.py lock --profile agents --profile memory
python3 scripts/toolchain.py lock --profile all --keep-going
```

## Synchronize local source

With a reviewed lock:

```bash
python3 scripts/toolchain.py sync --profile core
```

The compatibility wrapper performs the same locked core sync:

```bash
bash bootstrap-tools.sh
```

To update existing checkouts to the commits in a changed lock:

```bash
python3 scripts/toolchain.py sync --profile core --update
```

Unpinned research is possible only through an explicit escape hatch:

```bash
python3 scripts/toolchain.py sync --profile core --floating
```

Floating mode is useful for exploration and unsuitable as a reproducible build input.

## Failure behavior

The default is fail-fast. `--keep-going` attempts the rest of the selection and returns nonzero if any tool failed:

```bash
python3 scripts/toolchain.py sync --profile all --keep-going
```

Every run writes `state/tools-state.json` with successes, actual commit SHAs, and failures. A dirty checkout, unexpected origin URL, invalid catalog, missing lock entry, or failed Git command is surfaced rather than converted into a cheerful “done.”

## Profiles

Current profiles include:

- `core`
- `agents`
- `continual`
- `memory`
- `mcp`
- `code-intelligence`
- `binary-analysis`
- `cross-isa`
- `security-research`
- `runtime`
- `developer-tools`
- `reference`
- `all`

Presence in a profile means “worth evaluating,” not “approved to execute.”

## License and provenance

`license_hint` values in the catalog were carried forward from the previous credits file and remain **review-required** unless explicitly marked verified. Upstream licenses can change, dependencies can introduce additional terms, and local source cloning is not “binary-only use.”

Before modifying, redistributing, embedding, or exposing a tool as a service, review its exact locked commit and preserve all applicable notices. See [CREDITS.md](CREDITS.md).

## Pleiades integration boundary

This repository supplies candidates and exact source provenance. It should later feed:

- the polyglot package registry;
- reproducible Nix environments;
- isolated build/test sandboxes;
- the continual harness evaluation queue;
- signed integration manifests;
- the cognitive coprocessor's approved tool catalog.

No catalog entry should become a callable Pleiades capability merely because its repository cloned successfully.

## Related repositories

- [`pleiades`](https://github.com/Zheke32174/pleiades) — authority, policy, learning, and runtime architecture
- [`pleiades-container`](https://github.com/Zheke32174/pleiades-container) — Linux substrate
- [`pleiades-factory`](https://github.com/Zheke32174/pleiades-factory) — future private orchestration and promotion work
- [`pleiades-factory-stack-termux`](https://github.com/Zheke32174/pleiades-factory-stack-termux) — Android/Termux-specific adaptation

MIT — see [LICENSE](LICENSE). Third-party projects retain their own licenses.
