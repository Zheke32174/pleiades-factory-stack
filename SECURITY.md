# Security Policy

## Scope

This project is intended for authorized defensive research, local lab testing, decoy-service telemetry, and owner-authorized system administration.

Do not use this project on systems you do not own or administer without explicit permission.

## Reporting Issues

Please report security issues privately through GitHub Security Advisories when available, or by contacting the maintainer directly.

Do not open public issues containing:
- real credentials or tokens
- private logs or evidence archives
- exploit chains
- third-party host details
- personal information

## Secret Handling

Never commit:
- `.env` files
- API keys or OAuth tokens
- SSH private keys
- GitHub PATs
- Cloud credentials
- Private evidence archives

## Defensive-Use Boundary

This project does not authorize stealth deployment, credential theft, lateral movement, unauthorized reconnaissance, or evasion of a system owner or administrator.
