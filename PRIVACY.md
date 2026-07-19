# Privacy and Data Behavior

Pleiades Factory Stack does not include telemetry, analytics, advertising, account tracking, or a hosted service.

## Local data

When an operator runs synchronization commands, the utility may create:

- third-party Git checkouts under ignored `tools/`;
- a local synchronization receipt under ignored `state/tools-state.json`;
- a generated lock file at `catalog/tools.lock.json` when the operator explicitly runs `lock`;
- source-package output under a chosen `dist/` directory.

The state receipt can contain local filesystem paths, selected profiles/tools, upstream URLs, commit identities, and error text. Treat it as local operational data. It is ignored by Git and should not be attached to public issues without review and redaction.

## Network behavior

The following commands are network-free when their referenced files are already present:

- `validate`;
- `plan`;
- unit tests;
- public-tree/history scanning;
- source-package and SPDX generation.

`lock` contacts the Git hosts named in the selected catalog entries to resolve upstream refs. `sync` contacts those hosts to clone or fetch source. The utility does not send information to a Pleiades server, analytics provider, or maintainer endpoint.

Third-party Git hosts can observe ordinary connection metadata, including source IP address, requested repository, timing, and Git client behavior. Their privacy policies apply independently.

## Retention and deletion

The utility has no background process and no remote data-retention service.

To remove local data, delete:

- `tools/` for cloned third-party source;
- `state/` for synchronization receipts;
- generated `catalog/tools.lock.json` if the lock should not be retained;
- any chosen package-output directory.

Deleting the repository checkout removes the utility itself. No system-wide uninstall step is required.

## Sensitive information

Do not add credentials, private topology, personal information, private logs, or evidence to the public catalog, lock, state examples, documentation, tests, issues, or releases. Use synthetic examples and redact operational receipts before sharing them.
