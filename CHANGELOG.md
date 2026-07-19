# Changelog

This project follows semantic versioning for the Pleiades-owned catalog/synchronization utility. Catalog contents and third-party project versions are governed separately by reviewed lock files.

## Unreleased

- Bind the public distribution contract to one canonical `VERSION`.
- Add current-tree and reachable-history sensitivity scanning.
- Add deterministic source packaging, SHA-256 verification, SPDX 2.3 source inventory, and exact-commit build receipts.
- Replace branch-triggered mutable showcase releases with immutable tag-only releases containing real assets.
- Clarify experimental maturity, acquisition, privacy, support, update, rollback, removal, and third-party boundaries.
- Strengthen lock provenance so reviewed pins can be bound to the catalog, URL, requested ref, and selection that produced them.

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

No `0.1.0` release is considered published until the tag-only workflow produces the named source archive and verification assets from the reviewed tag.
