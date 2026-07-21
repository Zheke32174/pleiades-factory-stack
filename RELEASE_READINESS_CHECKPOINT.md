# Public release-readiness checkpoint

This ledger is the durable continuation point for public-release review of `Zheke32174/pleiades-factory-stack`. Update this file rather than recreating completed analysis in chat or parallel pull requests.

## Repository identity

- Repository: `Zheke32174/pleiades-factory-stack`
- Public distribution draft: PR #4, branch `hardening/public-distribution-readiness-v1`
- Stack base: PR #3, branch `codex/followup-selection-bootstrap-20260718`
- Last reviewed implementation head before this checkpoint: `94eab36d3faee67380a15373c00529a91ed4dfcf`
- Current checkpoint head: produced by the commit adding this ledger; inspect PR #4 for the exact SHA
- Release component: source catalog, lock, profile planning, and synchronization utility only
- Current disposition: `HOLD — EXACT-HEAD VALIDATION PENDING`

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

## Prior validation receipts

- PR #8 exact head `731b987bc250b2a833433da54f7f46375f1eaf94`: CI run #47 completed successfully, including Python compilation, unit tests, catalog validation, profile planning, public tree/history scan, deterministic source packaging, checksums, and artifact publication.
- PR #4 prior head `94eab36d3faee67380a15373c00529a91ed4dfcf`: previously reviewed public-distribution implementation; exact validation for the new Action pinning, attestation, ancestry, and release-note changes is pending.

A green result from another branch or an earlier head is not evidence for the current PR #4 head.

## Open blockers

1. Exact-head CI must execute and pass after the Action-pinning and provenance changes.
2. The first disposable prerelease must prove the tag ancestry check, attestation publication, checksum verification, and download instructions against real GitHub Release assets.
3. Generated locks still need complete binding to exact catalog digest, upstream URL, requested ref, and recorded selection through the stacked lock/sync drafts.
4. Arbitrary remote refs still require exact matched-ref and annotated-tag object/peeled-commit semantics.
5. Submodule and language dependency identities are reported but are not recursively locked.
6. Repository-level branch/ruleset configuration cannot be proven from source alone and remains a steward/admin verification item.

## Resolved findings

- Mutable branch-triggered release behavior: resolved in draft.
- Moving `latest` image/publication claim: removed.
- Missing repository-built downloadable artifact: resolved in draft.
- Missing checksum, SPDX inventory, and build receipt: resolved in draft.
- Unpinned third-party workflow Actions: resolved in draft.
- Release asset provenance absent: resolved in draft through GitHub attestations.
- Checkout credential persistence during validation: disabled.
- Release tag not proven reachable from default branch: resolved in draft.
- Public README implied a private visitor dependency: resolved in draft.

## Deferred items

- OpenSSF Scorecard automation is deferred until the core draft stack is integrated and repository rules are intentionally configured. Adding another third-party workflow now would increase notification and dependency churn without resolving the current release blockers.
- CodeQL is deferred because the current codebase is mostly Python/shell and the immediate release boundary already has compilation, unit tests, deterministic packaging, sensitivity scanning, and exact source receipts. Reconsider after the stack stabilizes or if public adoption expands.
- No package registry publication is planned; the supported public artifact is a deterministic source archive.

## Reconsideration triggers

Reprocess this repository only when at least one occurs:

- PR #4, #6, or #8 head/base changes;
- exact-head CI or release validation changes state;
- a workflow Action advisory or trusted release changes;
- the sensitivity scanner reports a new finding;
- lock or sync semantics change;
- a public-facing maturity, support, install, package, or release claim changes;
- repository rules/branch protection evidence becomes available;
- an explicit steward request reopens a deferred item.

## Next action

Inspect CI for the exact PR #4 head created by this checkpoint. Repair only concrete failures. If CI passes, keep PR #4 draft and HOLD until the stacked lock/sync dependencies and a disposable prerelease receipt are ready. Do not publish a tag or release merely to test the workflow without explicit steward authorization.
