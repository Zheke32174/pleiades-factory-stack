# Contributing

Pleiades Factory Stack accepts narrowly scoped improvements to catalog validation, lock integrity, reproducibility, documentation, tests, and source-synchronization behavior.

## Before opening a change

- Work from a clean checkout and a dedicated branch.
- Do not commit generated `tools/`, local `state/`, credentials, private topology, personal data, or operational evidence.
- Keep catalog additions separate from execution or integration proposals.
- Do not mark a third-party license as verified without reviewing the exact upstream source and preserving the evidence for that conclusion.
- Avoid moving upstream refs or floating dependencies in tests and release inputs.

## Required local checks

```bash
python3 -m py_compile scripts/toolchain.py scripts/write_spdx_sbom.py ci/scan_public_repo.py
python3 scripts/toolchain.py validate
python3 -m unittest discover -s tests -v
python3 ci/scan_public_repo.py
bash scripts/package_source.sh dist
(cd dist && sha256sum -c SHA256SUMS.txt)
```

A pull request should explain:

- the problem being corrected;
- the authority and data boundary affected;
- whether catalog, lock, state, package, or release schemas change;
- tests added or updated;
- migration and rollback behavior;
- any third-party license or provenance impact.

## Catalog changes

For a new or changed entry, record:

- canonical HTTPS upstream URL;
- category and bounded profiles;
- requested ref, or `null` when resolving upstream `HEAD` deliberately;
- license hint and review state;
- why the project is relevant for evaluation.

Catalog presence means evaluation interest only. Do not add build, install, service, or execution behavior to this repository as a side effect of cataloging a project.

## Compatibility

Schema changes require tests and clear migration notes. Release identities are immutable. Do not edit an existing release to point at a different commit or replace an existing asset under the same version.

## Support expectations

This is a small experimental project. Public issues may be used for reproducible non-sensitive bugs and documentation problems. Security-sensitive reports belong in GitHub's private vulnerability-reporting channel when available. No response-time, compatibility, or long-term maintenance guarantee is offered.
