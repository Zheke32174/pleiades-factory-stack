# Credits and Third-Party Attribution

Every external project, developer, or organization whose work is cloned,
installed, wrapped, or referenced by pleiades-factory-stack is listed here.

**No third-party source code is vendored in this repository.** All tools are
cloned or installed from upstream at setup time via `bootstrap-tools.sh`.
See `THIRD_PARTY_NOTICES.md` for the formal statement.

---

## Binary Lifting / Reverse Engineering

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| angr | angr project | BSD-2-Clause | https://github.com/angr/angr | cloned at setup time | No | No | N/A |
| ghidra | NSA / National Security Agency | Apache-2.0 | https://github.com/NationalSecurityAgency/ghidra | cloned at setup time | No | No | N/A |
| remill | Trail of Bits | Apache-2.0 | https://github.com/lifting-bits/remill | cloned at setup time | No | No | N/A |
| mcsema | Trail of Bits | Apache-2.0 | https://github.com/lifting-bits/mcsema | cloned at setup time | No | No | N/A |
| ddisasm | GrammaTech | **AGPL-3.0** | https://github.com/GrammaTech/ddisasm | cloned at setup time — **AGPL; binary-only use, no source vendored** | No | No | N/A |
| retrowrite | HexHive (EPFL) | MIT | https://github.com/HexHive/retrowrite | cloned at setup time | No | No | N/A |
| revng | rev.ng Labs | **GPL-2.0** | https://github.com/revng/revng | cloned at setup time — **GPL-2.0; binary-only use, no source vendored** | No | No | N/A |
| resym | lt-asset | MIT | https://github.com/lt-asset/resym | cloned at setup time | No | No | N/A |
| rmux | Helvesec | MIT | https://github.com/Helvesec/rmux | cloned at setup time | No | No | N/A |

## Cross-ISA Emulation

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| FEX | FEX-Emu | MIT | https://github.com/FEX-Emu/FEX | cloned at setup time | No | No | N/A |
| box64 | ptitSeb (Sebastian Chevalier) | MIT | https://github.com/ptitSeb/box64 | cloned at setup time | No | No | N/A |

## AI Agents / Frameworks

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| OpenHands | All-Hands-AI | MIT | https://github.com/All-Hands-AI/OpenHands | cloned at setup time | No | No | N/A |
| hermes-agent-self-evolution | NousResearch | Apache-2.0 | https://github.com/NousResearch/hermes-agent-self-evolution | cloned at setup time | No | No | N/A |
| CoEvoSkills | Zhang-Henry | MIT | https://github.com/Zhang-Henry/CoEvoSkills | cloned at setup time | No | No | N/A |
| SkillGen | yccm | MIT | https://github.com/yccm/SkillGen | cloned at setup time | No | No | N/A |
| SkillX | zjunlp | Apache-2.0 | https://github.com/zjunlp/SkillX | cloned at setup time | No | No | N/A |
| continual-harness | sethkarten | MIT | https://github.com/sethkarten/continual-harness | cloned at setup time | No | No | N/A |
| elephant-agent | agentic-in | Apache-2.0 | https://github.com/agentic-in/elephant-agent | cloned at setup time | No | No | N/A |
| agent-oss | quarqlabs | MIT | https://github.com/quarqlabs/agent-oss | cloned at setup time | No | No | N/A |
| claude-p | smithersai | MIT | https://github.com/smithersai/claude-p | cloned at setup time | No | No | N/A |
| CodexSaver | fendouai | MIT | https://github.com/fendouai/CodexSaver | cloned at setup time | No | No | N/A |
| ShadowCat | unprovable | MIT | https://github.com/unprovable/ShadowCat | cloned at setup time | No | No | N/A |
| piia-engram | Patdolitse | MIT | https://github.com/Patdolitse/piia-engram | cloned at setup time | No | No | N/A |
| Photo-agents | jmerelnyc | MIT | https://github.com/jmerelnyc/Photo-agents | cloned at setup time | No | No | N/A |

## Memory / Context

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| MemOS | MemTensor | Apache-2.0 | https://github.com/MemTensor/MemOS | cloned at setup time | No | No | N/A |
| ai-memory | akitaonrails | MIT | https://github.com/akitaonrails/ai-memory | cloned at setup time | No | No | N/A |
| DeepCode | HKUDS | MIT | https://github.com/HKUDS/DeepCode | cloned at setup time | No | No | N/A |

## MCP / API Integration

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| jcodemunch-mcp | jgravelle | MIT | https://github.com/jgravelle/jcodemunch-mcp | cloned at setup time; wrapped as MCP server | No | No | N/A |
| fastmcp | jlowin (Jeremiah Lowin) | Apache-2.0 | https://github.com/jlowin/fastmcp | installed via pip; used as MCP server framework in generated servers | No | No | N/A |
| fastapi_mcp | tadata-org | MIT | https://github.com/tadata-org/fastapi_mcp | installed via pip; optional integration | No | No | N/A |
| openapi-mcp-codegen | cnoe-io | Apache-2.0 | https://github.com/cnoe-io/openapi-mcp-codegen | optional integration | No | No | N/A |
| files-sdk | haydenbleasel | MIT | https://github.com/haydenbleasel/files-sdk | cloned at setup time | No | No | N/A |

## Code Analysis / Intelligence

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| paper2code | PrathamLearnsToCode | MIT | https://github.com/PrathamLearnsToCode/paper2code | cloned at setup time | No | No | N/A |
| codegraph | colbymchenry | MIT | https://github.com/colbymchenry/codegraph | cloned at setup time | No | No | N/A |
| codeindex | scheidydude | MIT | https://github.com/scheidydude/codeindex | cloned at setup time | No | No | N/A |
| repomix | yamadashy | MIT | https://github.com/yamadashy/repomix | installed via npm; used by `pleiades-mcp-converters.sh` for repo context packing | No | No | N/A |
| gitingest | coderamp-labs | MIT | https://github.com/coderamp-labs/gitingest | installed via pip; optional fallback for repo context packing | No | No | N/A |
| smallcode | Doorman11991 | MIT | https://github.com/Doorman11991/smallcode | cloned at setup time | No | No | N/A |
| auto-identity-remove | stephenlthorn | MIT | https://github.com/stephenlthorn/auto-identity-remove | cloned at setup time | No | No | N/A |

## Security / Offensive Research

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| LUKSbox | PentHertz | **GPL-3.0** | https://github.com/PentHertz/LUKSbox | cloned at setup time — **GPL-3.0; binary-only use, no source vendored** | No | No | N/A |
| opensquilla | OpenSquilla | MIT | https://github.com/OpenSquilla/opensquilla | cloned at setup time | No | No | N/A |

## Runtime / Language Runtimes

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| zerolang | Vercel Labs | MIT | https://github.com/vercel-labs/zerolang | cloned at setup time | No | No | N/A |
| zerostack | gi-dellav | MIT | https://github.com/gi-dellav/zerostack | cloned at setup time | No | No | N/A |
| btype | tidwall | MIT | https://github.com/tidwall/btype | cloned at setup time | No | No | N/A |
| chorus | chorus-codes | MIT | https://github.com/chorus-codes/chorus | cloned at setup time | No | No | N/A |

## Developer Tools

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| agent-rules-books | ciembor | MIT | https://github.com/ciembor/agent-rules-books | cloned at setup time | No | No | N/A |
| WSL | Microsoft | MIT | https://github.com/microsoft/WSL | referenced only — not cloned | No | No | N/A |
| auth.md | WorkOS | MIT | https://github.com/workos/auth.md | cloned at setup time | No | No | N/A |

## Framework References

| Project | Author / Org | License | Source URL | Usage Type | Vendored? | Modified? | Local Path |
|---------|-------------|---------|-----------|-----------|-----------|-----------|------------|
| agents-best-practices | DenisSergeevitch | MIT | https://github.com/DenisSergeevitch/agents-best-practices | structural reference in `AGENTS.md` — no source copied | No | No | N/A |

---

## Copyleft / AGPL Notice

The following tools carry copyleft licenses. In all cases, only the installed
binary is called — no source is vendored, modified, or redistributed:

| Project | License | Risk level | Handling |
|---------|---------|------------|---------|
| ddisasm | AGPL-3.0 | Medium — network-use copyleft may apply to modifications | Binary-only use; no source vendored |
| revng | GPL-2.0 | Medium — copyleft applies to modifications | Binary-only use; no source vendored |
| LUKSbox | GPL-3.0 | Medium — copyleft applies to modifications | Binary-only use; no source vendored |

If you modify or redistribute any of these tools as part of a derivative work,
review their license terms carefully before distribution.

---

## No Vendored Third-Party Source

This repository does not vendor source code from any third-party project.
Every tool listed above is cloned or installed from its upstream source at
setup time via `bootstrap-tools.sh`. See `THIRD_PARTY_NOTICES.md`.

> All trademarks and project names are property of their respective owners.
