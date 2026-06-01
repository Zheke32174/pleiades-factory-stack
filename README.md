# Pleiades Factory Tools & AI Stack

**Toolchain integration, LLM deployment, cross-ISA build pipeline, and research automation.**

Part of the [Pleiades](https://github.com/Zheke32174/pleiades) ecosystem — a WSL2/Gentoo systemd-nspawn security research and autonomous agent platform.

## Repositories

| Repo | Purpose |
|------|---------|
| [pleiades](https://github.com/Zheke32174/pleiades) | Host scripts, task master, toolchain orchestrator |
| [pleiades-container](https://github.com/Zheke32174/pleiades-container) | Gentoo nspawn container — agent stack deployment |
| **pleiades-factory-stack** (this repo) | Factory tools, AI/LLM stack, cross-ISA toolchain |
| [pleiades-evidence](https://github.com/Zheke32174/pleiades-evidence) | Private — secured evidence archive |
| [underhall](https://github.com/Zheke32174/underhall) | Original Arch nspawn install layer |
| [undercity](https://github.com/Zheke32174/undercity) | Backup/restore tooling |

## Components

### Factory Tools

| Tool | Description |
|------|-------------|
| `pleiades-factory-tools.sh` | CLI orchestrator for all factory tools |
| `paper2code` | arXiv paper to implementation pipeline |
| `hermes-agent-self-evolution` | AI agent self-improvement harness |
| `continual-harness` | Continuous testing and evaluation framework |

### AI Stack

| Component | Description |
|-----------|-------------|
| LLM Quantization | GGUF/GPTQ model optimization for local inference |
| Cross-ISA Build | QEMU + Box64 multi-architecture compilation |
| Alien Package Bridge | Multi-distribution package conversion (deb + Gentoo) |

## Third-Party Credits & Licenses

This project integrates and builds upon several open-source projects:

### Core Tools
- **Hermes Agent** — AI agent framework by Nous Research ([github.com/NousResearch/hermes](https://github.com/NousResearch/hermes)) — MIT
- **Claude Code** — CLI coding agent by Anthropic ([docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code)) — Subject to Anthropic ToS
- **Codex CLI** — CLI coding agent by OpenAI ([github.com/openai/codex](https://github.com/openai/codex)) — Apache 2.0
- **Gemini CLI** — CLI coding agent by Google ([google-gemini.github.io](https://google-gemini.github.io)) — Google ToS

### LLM & AI
- **llama.cpp** — LLM inference ([github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)) — MIT
- **vLLM** — High-throughput LLM serving ([github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)) — Apache 2.0
- **lm-eval-harness** — LLM evaluation ([github.com/EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)) — MIT
- **DSPy** — Declarative LM programming ([github.com/stanfordnlp/dspy](https://github.com/stanfordnlp/dspy)) — MIT
- **Nous Research** — Model training and evaluation tools ([nousresearch.com](https://nousresearch.com)) — Various OSS licenses

### Cross-ISA & Emulation
- **QEMU** — Machine emulator ([qemu.org](https://qemu.org)) — GPL v2
- **Box64** — x86_64 emulator for ARM64 ([github.com/ptitSeb/box64](https://github.com/ptitSeb/box64)) — MIT
- **FEX** — x86 emulator for ARM ([github.com/FEX-Emu/FEX](https://github.com/FEX-Emu/FEX)) — MIT

### Package Management
- **Gentoo Linux** — Source-based distribution ([gentoo.org](https://gentoo.org)) — GPL v2
- **Portage** — Package management system ([wiki.gentoo.org](https://wiki.gentoo.org/wiki/Portage)) — GPL v2

### Research & Development
- **arXiv** — Open access to scholarly articles ([arxiv.org](https://arxiv.org)) — Cornell University
- **Weights & Biases** — ML experiment tracking ([wandb.ai](https://wandb.ai)) — MIT (client)

## Getting Started

```bash
# List available factory tools
bash scripts/pleiades-factory-tools.sh list

# Check tool installation status
bash scripts/pleiades-factory-tools.sh status
```

## License

The Pleiades-sourced content in this repository is provided under the MIT License. Each integrated third-party component is subject to its own license as noted in the credits above.
