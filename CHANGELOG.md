# Changelog

This project follows semantic versioning for the Pleiades-owned catalog/synchronization utility. Catalog contents and third-party project versions are governed separately by reviewed lock files.

## Unreleased

- Bind generated locks to the exact catalog digest, upstream URL, requested ref, and recorded selection.
- Complete the first disposable `v0.2.0` publication exercise and verify every attached asset.

## 0.2.0

Public distribution and provenance hardening:

- add one canonical `VERSION`;
- add current-tree and reachable-history sensitivity scanning;
- add deterministic source packaging, SHA-256 verification, SPDX 2.3 source inventory, and exact-commit build receipts;
- replace branch-triggered mutable showcase releases with immutable tag-only releases containing real assets;
- clarify experimental maturity, acquisition, privacy, support, update, rollback, removal, and third-party boundaries;
- preserve `v0.1.0` as historical identity rather than overwriting it with a different release.

`0.2.0` is not considered published until the tag-only workflow produces and verifies the named source archive and accompanying verification assets from the reviewed tag.

## 0.1.0

Initial public source-catalog utility:

- manifest-driven catalog validation;
- bounded profile and named-tool selection;
- exact upstream commit lock generation;
- detached pinned source synchronization;
- wrong-origin and dirty-tree rejection;
- explicit floating-mode escape hatch;
- local synchronization receipts;
- third-party license and provenance notices.

The existing `v0.1.0` tag predates the immutable asset-bearing release contract. It must not be edited or reused as the verified `0.2.0` release.
