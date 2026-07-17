# Third-Party Credits and Review Status

Pleiades Factory Stack is a **manifest and synchronization layer** for third-party research projects. It does not vendor those projects into this repository, but it does clone their source code into a local ignored `tools/` directory when an operator requests it.

The canonical inventory is [`catalog/tools.catalog.json`](catalog/tools.catalog.json). Each entry records:

- project name;
- upstream HTTPS URL;
- functional category and optional profiles;
- an optional pinned ref;
- a license hint carried forward from the earlier catalog;
- an explicit license-review state.

## Important license boundary

A `license_hint` is not a legal conclusion and is not treated as verified unless the catalog explicitly says `"license_review": "verified"`.

Before a tool is:

- modified;
- embedded into Pleiades;
- redistributed;
- exposed as a network service;
- used to produce a public derivative artifact;

review the upstream repository's current license, notices, dependency licenses, and release-specific terms. Preserve upstream attribution and notices.

Cloning source locally does **not** mean that only a binary is being used. Earlier documentation described several copyleft projects as “binary-only” even though `bootstrap-tools.sh` cloned their source repositories. That wording was incorrect and has been removed.

## Copyleft and network-use licenses

Projects whose catalog hints include AGPL or GPL require special attention. Local research use, modification, distribution, and network deployment can carry different obligations. Do not merge their code into Pleiades or ship modified copies until the applicable obligations are documented for that exact use.

## Reproducibility and provenance

Normal synchronization should use a committed [`catalog/tools.lock.json`](catalog/tools.lock.json) containing exact 40-character commit SHAs. Floating clones require an explicit `--floating` flag and are unsuitable as reproducible build inputs.

Every synchronization writes `state/tools-state.json` containing the actual checked-out commit, action, category, and recorded license-review state. That file is local operational state and is not committed.

## No execution authorization

Presence in the catalog authorizes only cataloging and, when explicitly requested, cloning. It does not authorize building, executing, installing, exposing, or granting capabilities to a project. Those decisions belong to separate reviewed integration manifests and Pleiades policy.

## Complete inventory

For the current complete project list, categories, upstream URLs, profiles, and review states, see:

- [`catalog/tools.catalog.json`](catalog/tools.catalog.json)
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

All trademarks and project names remain the property of their respective owners.
