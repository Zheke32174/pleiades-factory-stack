# Public release-readiness checkpoint

This ledger is the durable continuation point for public-release review of `Zheke32174/pleiades-factory-stack`. Update this file rather than recreating completed analysis in chat or parallel pull requests.

## Repository identity

- Repository: `Zheke32174/pleiades-factory-stack`
- Public distribution draft: PR #4, branch `hardening/public-distribution-readiness-v1`
- Stack base: PR #3, branch `codex/followup-selection-bootstrap-20260718`
- Last fully validated implementation head: `95f87b80183386b44c24d0aac158858ce7d50fed`
- Current ledger head: produced by this receipt-only update; inspect PR #4 for the exact SHA
- Release component: source catalog, lock, profile planning, and synchronization utility only
- Current disposition: `HOLD — STACKED DEPENDENCIES AND PRERELEASE RECEIPT PENDING`

## Completed scope

- Replaced branch-triggered mutable showcase publication with matching immutable version tags.
- Builds a named deterministic source archive twice and byte-compares every generated asset.
- Emits SHA-256 checksums, SPDX 2.3 source inventory, and an exact-commit build receipt.
- Refuses to overwrite an existing GitHub Release identity.
- Scans the current tracked tree and reachable Git history for configured sensitive patterns without echoing matched content.
- Rewrote visitor-facing documentation around experimental status, acquisition, quick start, failure behavior, privacy, security, update, rollback, removal, and third-party license boundaries.
- Removed the private orchestrator from the public visitor path.
- Full-length commit-SHA pinned all third-party Actions used by CI and release workflows.
- Disabled persisted checkout credentials in read-only and release validation checkouts.
- Added GitHub artifact attestations for the source archive, SPDX inventory, build receipt, and checksum manifest.
- Added default-branch ancestry validation before tag publication.
- Added checksum and provenance verification commands to release notes.

## External comparison provenance

Reviewed on 2026-07-20:

- GitHub Secure Use Reference: full-length Action commit SHAs are the only immutable Action references.
- OpenSSF Scorecard: high-value public-release checks include least-privilege workflow tokens, pinned dependencies, branch protection, CI tests, security policy, packaging, and signed or attested releases.
- Existing `Zheke32174/pleiades` draft release path: validated local precedent for deterministic assets, exact commit receipts, immutable Action references, provenance attestations, and download-first verification instructions.

No external source code was copied. The practices were adapted to this repository's narrower source-catalog distribution boundary.

## Trusted workflow identities

- `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` — v7.0.1
- `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02` — v4.6.2
- `actions/attest@a1948c3f048ba23858d222213b7c278aabede763` — v4.1.1

Reconsider only when upstream security guidance changes, a trusted release is withdrawn, an advisory affects one of these identities, or a deliberate upgrade is reviewed.

## Validation receipts

- PR #8 exact head `731b987bc250b2a833433da54f7f46375f1eaf94`: CI run #47 completed successfully, including Python compilation, unit tests, catalog validation, profile planning, public tree/history scan, deterministic source packaging, checksums, and artifact publication.
- PR #4 exact head `95f87b80183386b44c24d0aac158858ce7d50fed`: CI run `29789787170` completed successfully.
  - `verify` job: immutable checkout action executed; Python/shell compilation passed; catalog validation passed; unit tests passed; profile planning passed; public tree/history scan passed; repository boundary checks passed.
  - `source-package` job: immutable checkout action executed; two builds compared byte-for-byte; checksum verification passed; exact-head candidate artifact uploaded.
- The tag-only release and attestation path has not been executed. CI success does not prove release publication or attestation behavior.

The ledger-only commit following the validated head does not change executable or workflow behavior; nevertheless, the exact workflow receipt remains bound to `95f87b8...`.

## Open blockers

1. The first explicitly authorized disposable prerelease must prove tag ancestry, attestation publication, checksum verification, download instructions, and release overwrite refusal against real GitHub Release assets.
2. Generated locks still need complete binding to exact catalog digest, upstream URL, requested ref, and recorded selection through the stacked lock/sync drafts.
3. Arbitrary remote refs still require exact matched-ref and annotated-tag object/peeled-commit semantics.
4. Submodule and language dependency identities are reported but are not recursively locked.
5. Repository-level branch/ruleset configuration cannot be proven from source alone and remains a steward/admin verification item.

## Resolved findings

- Mutable branch-triggered release behavior: resolved in draft.
- Moving `latest` image/publication claim: removed.
- Missing repository-built downloadable artifact: resolved in draft.
- Missing checksum, SPDX inventory, and build receipt: resolved in draft.
- Unpinned third-party workflow Actions: resolved in draft and exact-head CI validated.
- Release asset provenance absent: resolved in draft through GitHub attestations; live tag receipt pending.
- Checkout credential persistence during validation: disabled and exact-head CI validated.
- Release tag not proven reachable from default branch: resolved in draft; live tag receipt pending.
- Public README implied a private visitor dependency: resolved in draft.

## Deferred items

- OpenSSF Scorecard automation is deferred until the core draft stack is integrated and repository rules are intentionally configured. Adding another third-party workflow now would increase notification and dependency churn without resolving the current release blockers.
- CodeQL is deferred because the current codebase is mostly Python/shell and the immediate release boundary already has compilation, unit tests, deterministic packaging, sensitivity scanning, and exact source receipts. Reconsider after the stack stabilizes or if public adoption expands.
- No package registry publication is planned; the supported public artifact is a deterministic source archive.

## Reconsideration triggers

Reprocess this repository only when at least one occurs:

- PR #4, #6, or #8 head/base changes;
- release-path validation changes state;
- a workflow Action advisory or trusted release changes;
- the sensitivity scanner reports a new finding;
- lock or sync semantics change;
- a public-facing maturity, support, install, package, or release claim changes;
- repository rules/branch protection evidence becomes available;
- explicit authorization is given for a disposable prerelease;
- an explicit steward request reopens a deferred item.

## Next action

Skip ordinary reprocessing until a trigger occurs. The next substantive checkpoint is stacked dependency integration in order or an explicitly authorized disposable prerelease. Do not publish a tag or release merely to exercise the workflow without steward authorization.
