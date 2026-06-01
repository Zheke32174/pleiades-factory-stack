# Pleiades Factory Stack

Toolchain integration, LLM deployment, cross-ISA build pipeline, and research automation helpers.

Part of the [Pleiades](https://github.com/Zheke32174/pleiades) ecosystem — an owner-authorized defensive container lab.

## Repository Map

| Repo | Purpose |
|------|---------|
| [`pleiades`](https://github.com/Zheke32174/pleiades) | Host scripts and agent suite |
| [`pleiades-container`](https://github.com/Zheke32174/pleiades-container) | Gentoo `systemd-nspawn` container layer |
| **`pleiades-factory-stack`** (this repo) | Tooling, AI/LLM integration, cross-ISA research helpers |
| `pleiades-evidence` | Private evidence archive — never public |

## What's Here

```
bootstrap-tools.sh   — clones all third-party tools from upstream; safe to re-run
CREDITS.md           — full attribution for all third-party projects
docs/                — architecture and integration notes
```

## Getting Started

```bash
# Clone all third-party tools from their upstream repos
bash bootstrap-tools.sh

# Update existing tool clones
bash bootstrap-tools.sh --update
```

## Tool Categories

- **Binary lifting / reverse engineering** — angr, Ghidra, remill, mcsema, ddisasm, RetroWrite, rev.ng
- **Cross-ISA emulation** — FEX, Box64
- **AI agents and evaluation harnesses** — OpenHands, Hermes, CoEvoSkills, SkillGen, SkillX
- **Memory and context** — MemOS, DeepCode, ai-memory
- **MCP / API integration** — jcodemunch-mcp, fastmcp, fastapi-mcp, openapi-mcp-codegen
- **Code analysis** — paper2code, repomix, codegraph, gitingest
- **Security research** — LUKSbox, opensquilla

See [CREDITS.md](CREDITS.md) for the complete list with licenses and upstream sources.

## Vendoring Status

This repository does **not** vendor third-party tools. `bootstrap-tools.sh` clones each tool from its upstream repository at setup time. No third-party source code is committed here.

Each component remains governed by its upstream license. Review [CREDITS.md](CREDITS.md) before use in your context.

## Credential Statement

Credentials were stripped before this public push. API keys, tokens, and secrets exist only in the local operator environment.

Never commit:
- `.env` files or environment variable dumps
- API keys, OAuth tokens, or GitHub PATs
- SSH private keys or certificates
- Model provider credentials
- Private evidence archives

## License

MIT — see [LICENSE](LICENSE).

## Security

See [SECURITY.md](SECURITY.md).
