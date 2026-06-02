# Pleiades Factory Stack

Bootstrap scripts and configuration for the Pleiades research toolchain: binary analysis, cross-ISA emulation, and AI/LLM agent integration. Run `bootstrap-tools.sh` to clone all third-party tools from their upstream repos.

Part of the [Pleiades](https://github.com/Zheke32174/pleiades) ecosystem.

## Repository Map

| Repo | Status | Purpose |
|------|--------|---------|
| [`pleiades`](https://github.com/Zheke32174/pleiades) | Release-track | Host scripts and agent suite |
| [`pleiades-container`](https://github.com/Zheke32174/pleiades-container) | Release-track | Gentoo `systemd-nspawn` container layer |
| **`pleiades-factory-stack`** (this repo) | Release-track | Tooling, AI/LLM integration, cross-ISA research helpers |
| `pleiades-factory` | Private staging | Future factory orchestration work; not public-ready yet |
| `pleiades-evidence` | Private forever | Forensic evidence archive — never public |

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

## Vendoring

No third-party source code is committed here. `bootstrap-tools.sh` clones each tool from its upstream repo at setup time, so each component stays governed by its own license. Review [CREDITS.md](CREDITS.md) before use.

## Secrets and Credentials

No credentials or secrets are committed to this repository. If you fork it, keep `.env` files, API keys, OAuth tokens, SSH keys, and private evidence archives out of version control.

## AI Assistance

Documentation and scaffolding were partly drafted with Claude (Anthropic) and ChatGPT (OpenAI). Every third-party tool still needs to be credited to its original author regardless of how scaffolding was generated — see [CREDITS.md](CREDITS.md).

---

MIT — [LICENSE](LICENSE) · [SECURITY.md](SECURITY.md)
