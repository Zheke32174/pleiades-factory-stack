# Third-Party Notices

## No Vendored Source

This repository does not contain vendored third-party source code.

All external tools referenced by pleiades-factory-stack are:
- Cloned from their upstream repositories via `bootstrap-tools.sh`, OR
- Installed from official package registries (pip, npm, cargo, apt, etc.)

No third-party source files are committed to this repository. Each external
project remains entirely governed by its own license.

## Runtime Dependencies Cloned at Setup

The following projects are cloned when `bootstrap-tools.sh` is run.
They are never present in this repository.

| Project | Upstream URL | License |
|---------|-------------|---------|
| angr | https://github.com/angr/angr | BSD-2-Clause |
| ghidra | https://github.com/NationalSecurityAgency/ghidra | Apache-2.0 |
| remill | https://github.com/lifting-bits/remill | Apache-2.0 |
| mcsema | https://github.com/lifting-bits/mcsema | Apache-2.0 |
| ddisasm | https://github.com/GrammaTech/ddisasm | AGPL-3.0 |
| retrowrite | https://github.com/HexHive/retrowrite | MIT |
| revng | https://github.com/revng/revng | GPL-2.0 |
| resym | https://github.com/lt-asset/resym | MIT |
| FEX | https://github.com/FEX-Emu/FEX | MIT |
| box64 | https://github.com/ptitSeb/box64 | MIT |
| OpenHands | https://github.com/All-Hands-AI/OpenHands | MIT |
| hermes-agent-self-evolution | https://github.com/NousResearch/hermes-agent-self-evolution | Apache-2.0 |
| CoEvoSkills | https://github.com/Zhang-Henry/CoEvoSkills | MIT |
| SkillGen | https://github.com/yccm/SkillGen | MIT |
| SkillX | https://github.com/zjunlp/SkillX | Apache-2.0 |
| continual-harness | https://github.com/sethkarten/continual-harness | MIT |
| elephant-agent | https://github.com/agentic-in/elephant-agent | Apache-2.0 |
| agent-oss | https://github.com/quarqlabs/agent-oss | MIT |
| MemOS | https://github.com/MemTensor/MemOS | Apache-2.0 |
| ai-memory | https://github.com/akitaonrails/ai-memory | MIT |
| DeepCode | https://github.com/HKUDS/DeepCode | MIT |
| jcodemunch-mcp | https://github.com/jgravelle/jcodemunch-mcp | MIT |
| fastmcp | https://github.com/jlowin/fastmcp | Apache-2.0 |
| paper2code | https://github.com/PrathamLearnsToCode/paper2code | MIT |
| repomix | https://github.com/yamadashy/repomix | MIT |
| gitingest | https://github.com/coderamp-labs/gitingest | MIT |
| LUKSbox | https://github.com/PentHertz/LUKSbox | GPL-3.0 |
| opensquilla | https://github.com/OpenSquilla/opensquilla | MIT |

## License Compatibility

pleiades-factory-stack scripts are MIT-licensed. Because no third-party source
is vendored, there are no GPL/AGPL mixing concerns in this repository.

The following tools have copyleft licenses — only their binaries are called,
no source is vendored or modified:

| Project | License | Note |
|---------|---------|------|
| ddisasm | AGPL-3.0 | Binary-only use |
| revng | GPL-2.0 | Binary-only use |
| LUKSbox | GPL-3.0 | Binary-only use |

If you vendor any of these tools into a derivative work, review the
compatibility of their licenses with your distribution terms.
