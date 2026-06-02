# Pleiades Factory Stack

Toolchain integration, LLM deployment, cross-ISA build pipeline, and research automation helpers.

Part of the [Pleiades](https://github.com/Zheke32174/pleiades) ecosystem — a defensive container lab for host-protection research and forensic evidence collection.

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

This repository does **not** vendor third-party tools. `bootstrap-tools.sh` clones each tool from its upstream repository at setup time. No third-party source code is committed here.

Each component is governed by its upstream license. Review [CREDITS.md](CREDITS.md) before use in your context.

## Secrets and Credentials

No credentials, API keys, tokens, or secrets are committed to this repository. If you fork or adapt this project, never commit:

- `.env` files or environment variable dumps
- API keys or OAuth tokens
- SSH private keys or certificates
- Model provider credentials
- Private evidence archives

## AI Assistance Disclosure

Parts of this project's documentation, planning notes, cleanup checklists, and script scaffolding were developed with assistance from AI tools, including Claude by Anthropic and ChatGPT by OpenAI.

Human maintainers are responsible for reviewing, testing, security boundaries, attribution, and final repository contents. AI assistance does not replace upstream attribution — every third-party tool must still be credited to its original developer or organization.

## License

MIT — see [LICENSE](LICENSE).

## Security

See [SECURITY.md](SECURITY.md).
