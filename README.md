# Pleiades Factory Stack

> **Status:** experimental but working source-catalog infrastructure. This is not a package manager, software store, or approval to execute the projects it catalogs.

Pleiades Factory Stack records which third-party research projects are worth evaluating, resolves exact upstream commits, and synchronizes reviewed source checkouts without silently treating mutable upstream branches as a reproducible toolchain.

## Get the tool

### Reviewed source release

Open the [GitHub Releases page](https://github.com/Zheke32174/pleiades-factory-stack/releases) and download the versioned file named:

`pleiades-factory-stack-<version>.tar.gz`

Each proper release also includes:

- `SHA256SUMS.txt`;
- an SPDX 2.3 JSON source inventory;
- an exact-commit build receipt.

**Current publication state:** no permanent public release is considered valid until the tag-only release workflow has produced and verified those assets. Pull-request artifacts are review candidates, not releases.

### Reviewed checkout

A clean checkout is also supported:

```bash
git clone https://github.com/Zheke32174/pleiades-factory-stack.git
cd pleiades-factory-stack
python3 scripts/toolchain.py validate
```

Requirements are Python 3.9 or newer, Git, and a POSIX-like shell for the compatibility wrapper and source-package script. Bare Linux and WSL are both supported development substrates. Termux-specific adaptation lives in `pleiades-factory-stack-termux`.

## What the repository owns

The repository separates four concerns:

- **catalog** — projects considered relevant and why;
- **lock** — exact upstream commits selected for a reproducible checkout;
- **local state** — what is actually present under `tools/`;
- **integration** — a later, separately reviewed decision to build, execute, package, or expose a tool.

The current implementation:

- validates tool names, profiles, categories, HTTPS upstream URLs, and review metadata;
- supports bounded functional profiles instead of cloning every project by default;
- resolves exact upstream commit SHAs into a reviewed lock file;
- checks out pinned commits in detached HEAD state;
- rejects unexpected origins and dirty trees by default;
- records actual checkout commits and failures;
- requires `--floating` before following an unpinned upstream head;
- clones source only—it does not build, execute, install, or grant capabilities;
- scans the public tree and reachable Git history for configured credential, private-topology, and host-local patterns;
- builds deterministic source-release candidates with checksums, SPDX inventory, and an exact-commit receipt.

## Quick start without mutation

Validate the catalog:

```bash
python3 scripts/toolchain.py validate
```

Inspect the bounded default profile:

```bash
python3 scripts/toolchain.py plan
```

Inspect explicit selections. Explicit profiles or tools do not silently append `core`:

```bash
python3 scripts/toolchain.py plan --profile memory
python3 scripts/toolchain.py plan --profile binary-analysis
python3 scripts/toolchain.py plan --tool repomix
```

A fresh checkout intentionally has no generated lock. Running the compatibility wrapper in that state prints the non-mutating core plan and the exact lock command rather than resolving mutable upstream heads or failing halfway through bootstrap:

```bash
bash bootstrap-tools.sh
```

## Create and review a lock

Resolve the selected upstream refs:

```bash
python3 scripts/toolchain.py lock --profile core
```

Review and commit `catalog/tools.lock.json`. Lock generation is an explicit dependency update, not a routine-startup side effect.

Larger examples:

```bash
python3 scripts/toolchain.py lock --profile agents --profile memory
python3 scripts/toolchain.py lock --profile all --keep-going
```

## Synchronize source

With a reviewed lock:

```bash
python3 scripts/toolchain.py sync --profile core
```

To move existing clean checkouts to a changed reviewed lock:

```bash
python3 scripts/toolchain.py sync --profile core --update
```

Unpinned research requires an explicit escape hatch:

```bash
python3 scripts/toolchain.py sync --profile core --floating
```

Floating mode is unsuitable as a reproducible build input.

## Failure and local-state behavior

The default is fail-fast. `--keep-going` attempts the remaining selection and still returns nonzero if anything failed:

```bash
python3 scripts/toolchain.py sync --profile all --keep-going
```

Every synchronization run writes ignored `state/tools-state.json` with the requested selection, actual commits, successes, and failures. A dirty checkout, unexpected origin, invalid catalog, missing lock entry, or failed Git command is surfaced rather than converted into a cheerful completion message.

The tool performs no telemetry. It makes network requests only when the operator explicitly runs `lock` or `sync`; those commands contact the Git hosts named in the catalog. Locally cloned third-party repositories and state reports remain outside this repository unless an operator deliberately moves or commits them.

## Layout

```text
VERSION                         source-package version
catalog/tools.catalog.json      project inventory and review metadata
catalog/tools.lock.json         generated exact pins; absent until reviewed
scripts/toolchain.py            validate, plan, lock, and sync engine
bootstrap-tools.sh              compatibility wrapper for plan/locked sync
scripts/package_source.sh       reproducible source-package builder
scripts/write_spdx_sbom.py      exact-commit SPDX source inventory
ci/scan_public_repo.py          current-tree and reachable-history sensitivity gate
tools/                          local third-party source checkouts; ignored
state/tools-state.json          local synchronization receipt; ignored
CREDITS.md                      attribution and license-review boundary
THIRD_PARTY_NOTICES.md          third-party handling notice
```

## Profiles

Current profiles include `core`, `agents`, `continual`, `memory`, `mcp`, `code-intelligence`, `binary-analysis`, `cross-isa`, `security-research`, `runtime`, `developer-tools`, `reference`, `termux`, and `all`.

Presence in any profile means **worth evaluating**, not approved to execute.

## License and third-party provenance

The Pleiades-owned synchronization code is MIT licensed. Cataloged projects retain their own licenses, notices, trademarks, dependencies, and usage restrictions.

`license_hint` is informational unless the exact entry is explicitly marked verified. Before modifying, redistributing, embedding, hosting, or exposing a cataloged tool, review the exact locked commit and preserve every applicable notice. See [CREDITS.md](CREDITS.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

No source release from this repository is intended to bundle the cataloged third-party repositories themselves.

## Security, privacy, and support

- Security policy and supported-version posture: [SECURITY.md](SECURITY.md)
- Data and network behavior: [PRIVACY.md](PRIVACY.md)
- Contribution and support expectations: [CONTRIBUTING.md](CONTRIBUTING.md)
- Version history: [CHANGELOG.md](CHANGELOG.md)

Do not place credentials, private topology, local evidence, or personal data in a public issue. Use GitHub's private vulnerability-reporting channel when available.

## Update, rollback, and removal

To update the utility itself, check out a reviewed tag or commit and rerun validation. Lock updates are reviewed separately from utility updates.

To roll back, restore the previous reviewed utility commit and previous `catalog/tools.lock.json`. Because synchronized tools are detached at exact commits, a reviewed prior lock can restore their prior source identities.

To remove the utility, delete its checkout. To remove locally synchronized third-party source and local receipts, also delete the ignored `tools/` and `state/` directories. No system service, daemon, package database, or global configuration is installed by this repository.

## Pleiades boundary

This repository supplies source candidates and provenance. Catalog entries must pass separate licensing, security, build, evaluation, and promotion review before becoming callable Pleiades capabilities.

Related public repositories:

- [`pleiades`](https://github.com/Zheke32174/pleiades) — public contracts and bounded runtime architecture;
- [`pleiades-container`](https://github.com/Zheke32174/pleiades-container) — Linux substrate;
- [`pleiades-factory-stack-termux`](https://github.com/Zheke32174/pleiades-factory-stack-termux) — thin Termux source-profile adapter.

The private factory orchestrator is intentionally not a public dependency or visitor-facing installation target.
