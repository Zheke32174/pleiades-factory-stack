# Security Policy

## Project status

Pleiades Factory Stack is experimental source-catalog infrastructure. It is not a package manager, sandbox, trust broker, malware-analysis appliance, or approval service for the projects it catalogs.

Only the most recent reviewed source release and current default branch are eligible for security fixes. Historical tags, floating third-party heads, local `tools/` checkouts, and unreviewed lock files are unsupported.

## Report vulnerabilities privately

Use GitHub's private vulnerability-reporting or Security Advisory interface for this repository when available. Do not post exploitable details, credentials, private topology, personal data, or third-party evidence in a public issue.

A useful report includes:

- affected commit or release;
- exact command and catalog/lock selection;
- whether `--floating`, `--allow-dirty`, or `--keep-going` was used;
- expected and observed behavior;
- a minimal redacted reproducer;
- impact on origin validation, lock integrity, local state, filesystem boundaries, or release provenance.

No response-time or remediation-time guarantee is offered.

## Security boundaries

The utility is expected to:

- accept only reviewed catalog structure and HTTPS GitHub origins;
- surface command and synchronization failures;
- reject unexpected repository origins;
- reject dirty local checkouts unless the operator explicitly overrides that protection;
- require exact commit pins unless the operator explicitly chooses floating mode;
- keep cloned third-party source and local state out of this repository by default;
- avoid building, executing, installing, or granting authority to cataloged projects;
- publish source releases only from immutable version tags with checksums, source inventory, and an exact-commit receipt.

The utility does **not** protect an operator who deliberately enables floating mode, accepts an unreviewed lock, overrides dirty-tree checks, executes cloned third-party source, or runs it with excessive host permissions.

## Third-party risk

Catalog inclusion is not a security endorsement. A repository can change ownership, rewrite branches, alter dependencies, add generated binaries, or change license terms. Exact commit pinning improves repeatability but does not establish safety.

Before any cataloged project becomes executable or distributable, perform a separate review of the locked commit, dependency graph, build process, release provenance, network behavior, data access, license obligations, and deployment isolation.

## Credential and sensitive-data handling

Do not commit:

- API keys, tokens, passwords, cookies, OAuth material, or private keys;
- real `.env` files or secret-bearing configuration;
- private hostnames, tailnet identities, internal addresses, or stale private endpoints;
- personal data, logs, evidence, screenshots, crash dumps, or database snapshots;
- locally cloned `tools/` content or `state/tools-state.json`;
- realistic secret fixtures that scanners or users could mistake for live credentials.

CI scans the current tracked tree and reachable Git history for configured credential, private-topology, and host-local patterns. That scanner is a review aid, not proof that no sensitive information exists. If a real secret reached Git history, revoke or rotate it first; deleting the current file is not sufficient remediation.

## Release integrity

A valid release must:

1. originate from a tag equal to `v$(cat VERSION)`;
2. pass catalog validation, unit tests, and the public-history sensitivity scan;
3. build the source package from a clean exact commit;
4. include `SHA256SUMS.txt`, an SPDX 2.3 JSON inventory, and a build receipt;
5. refuse to overwrite an existing release identity.

GitHub's automatically generated source archives are not substitutes for the named release asset and verification files produced by the repository workflow.
