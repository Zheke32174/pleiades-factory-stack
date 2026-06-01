# Pleiades Factory Stack — AI/LLM Tool Framework

## agents-best-practices Framework

This repo follows the [agents-best-practices](https://github.com/DenisSergeevitch/agents-best-practices) framework.
All agent CLIs (Claude Code, Codex CLI, Gemini CLI, OpenCode) load this AGENTS.md on session start.

See the main [pleiades repo](https://github.com/Zheke32174/pleiades) for the cross-CLI harness rules.

## Architecture

### Tool Categories

| Category | Tools |
|----------|-------|
| Binary Analysis | angr, Ghidra, ddisasm, mcsema, remill, retrowrite, revng |
| Agent Frameworks | elephant-agent, opensquilla, zerostack, openhands, continual-harness |
| MCP/Connector | fastapi_mcp, fastmcp, jcodemunch-mcp, openapi-mcp-codegen, piia-engram |
| Agent Skills | CoEvoSkills, SkillGen, SkillX, CodexSaver |
| Emulation | box64, FEX, btype |
| Research Tools | paper2code, repomix, gitingest, codeindex |

### Cross-CLI Integration

Every tool is symlinked into all agent CLI skill directories:
- `~/.codex/skills/` — Codex CLI
- `~/.claude/skills/` — Claude Code
- `~/.gemini/skills/` — Gemini CLI

### MCP Servers

```json
{
    "mcpServers": {
        "jcodemunch-mcp": {
            "command": "python3",
            "args": [
                "-m",
                "jcodemunch_mcp"
            ],
            "env": {
                "JCODEMUNCH_HOME": "/workspaces/gentoo/tools/jcodemunch-mcp",
                "JCODEMUNCH_API_PORT": "37700"
            },
            "disabled": false,
            "autoApprove": []
        },
        "fastapi-mcp": {
            "command": "python3",
            "args": [
                "-m",
                "fastapi_mcp"
            ],
            "disabled": true,
            "autoApprove": []
        },
        "openapi-mcp-codegen": {
            "command": "python3",
            "args": [
                "-m",
                "openapi_mcp_codegen"
            ],
            "disabled": true,
            "autoApprove": []
        },
        "piia-engram": {
            "command": "python3",
            "args": [
                "-m",
                "piia_engram.mcp_server"
            ],
            "disabled": true,
            "autoApprove": []
        },
        "files-sdk": {
            "command": "node",
            "args": [
                "index.js"
            ],
            "disabled": true,
            "autoApprove": []
        }
    }
}
```

## Third-Party Accreditation

| Component | License | Description |
|-----------|---------|-------------|
| Heres Agent | MIT | Agent harness foundation |
| Claude Code | Anthropic ToS | Claude Code CLI by Anthropic |
| Codex CLI | MIT | OpenAI Codex CLI |
| Gemini CLI | Google ToS | Google Gemini CLI |
| OpenCode | MIT | Nous Research OpenCode CLI |
| agents-best-practices | MIT | Agent harness framework by DenisSergeevitch |
| elephant-agent | MIT | Agent framework by agentic-in |
| opensquilla | MIT | Token-efficient AI agent |
| zerostack | MIT | Minimal coding agent in Rust |
| OpenHands | MIT | AI software development agent |
| jcodemunch-mcp | MIT | Token-efficient code exploration MCP |
| fastapi_mcp | MIT | FastAPI to MCP bridge |
| fastmcp | MIT | MCP framework |
| SkillGen | MIT | Verified inference-time scaling |
| CoEvoSkills | MIT | Self-evolving skills |
| angr | BSD-2 | Binary analysis framework |
| Ghidra | Apache-2.0 | SRE framework by NSA |
| paper2code | MIT | arXiv paper to implementation converter |
| box64 | MIT | x86_64 emulation on ARM64 |
| FEX | MIT | x86 emulation on ARM64 |
| repomix | MIT | Repository code packaging |
| gitingest | MIT | Git repository ingestion |
| retrowrite | MIT | Static binary rewriting |

All third-party components are used in accordance with their respective licenses.
