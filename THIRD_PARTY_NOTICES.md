# Third-Party Notices

This repository contains Pleiades-owned cataloging and synchronization code. It does not commit the source trees of cataloged third-party projects.

When an operator runs the synchronization command, third-party **source repositories are cloned locally** into the ignored `tools/` directory. Those local checkouts remain governed by their upstream licenses, notices, trademarks, and dependency terms.

## Canonical inventory

The complete machine-readable inventory is:

- [`catalog/tools.catalog.json`](catalog/tools.catalog.json)
- optional exact pins in `catalog/tools.lock.json`
- local checkout evidence in ignored `state/tools-state.json`

The catalog's `license_hint` field is informational and carried forward from earlier project notes. It is not verified legal metadata unless the same entry is explicitly marked `"license_review": "verified"`.

## No automatic permission to use or ship

Cataloging or cloning a repository does not authorize:

- execution;
- installation;
- modification;
- redistribution;
- embedding into a Pleiades binary or image;
- exposing it as a network service;
- use outside the upstream project's license or acceptable-use restrictions.

Each proposed integration needs its own review of the exact locked commit, source and dependency licenses, notices, security posture, and intended deployment model.

## Copyleft and network-use obligations

Projects with GPL, AGPL, or other copyleft terms may impose obligations depending on modification, linking, distribution, and network deployment. The prior notice described several cloned source repositories as “binary-only use.” That description was inaccurate and has been removed.

Keep upstream license and notice files with any local or distributed copy. Before shipping a derivative, obtain a project-specific compatibility review rather than relying on the catalog hint.

## Provenance

For reproducible work, generate and review a lock file containing exact upstream commit SHAs:

```bash
python3 scripts/toolchain.py lock --profile core
python3 scripts/toolchain.py sync --profile core
```

Floating upstream heads require an explicit `--floating` flag and should not be treated as release inputs.

All trademarks and project names belong to their respective owners.
