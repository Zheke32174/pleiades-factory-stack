#!/data/data/com.termux/files/usr/bin/env bash
# bootstrap-tools.sh — Clone all third-party tools into tools/
source "${PLEIADES_TERMUX_LIB:-}" 2>/dev/null || true
set -euo pipefail

# Termux: override tools dir
if [[ "${PLEIADES_ENV:-}" == "termux" ]]; then
  TOOLS_DIR="${PLEIADES_TOOLS:-${HOME}/pleiades/tools}"
else
  TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/tools"
fi
UPDATE=false
[[ "${1:-}" == "--update" ]] && UPDATE=true

mkdir -p "$TOOLS_DIR"

log() { echo "[bootstrap-tools] $*"; }

clone_or_update() {
    local name="$1" url="$2"
    local dest="$TOOLS_DIR/$name"
    if [[ -d "$dest" ]]; then
        if $UPDATE; then
            log "Updating $name..."
            git -C "$dest" pull --ff-only --quiet 2>/dev/null || log "WARN: $name update failed (skipping)"
        else
            log "Skipping $name (already present; use --update to refresh)"
        fi
    else
        log "Cloning $name..."
        git clone --depth=1 "$url" "$dest" 2>/dev/null || log "WARN: $name clone failed"
    fi
}

# ── Binary Lifting / Reverse Engineering ────────────────────────────────────
clone_or_update angr              https://github.com/angr/angr.git
clone_or_update ghidra            https://github.com/NationalSecurityAgency/ghidra.git
clone_or_update remill            https://github.com/lifting-bits/remill.git
clone_or_update mcsema            https://github.com/lifting-bits/mcsema.git
clone_or_update ddisasm           https://github.com/GrammaTech/ddisasm.git
clone_or_update retrowrite        https://github.com/HexHive/retrowrite.git
clone_or_update revng             https://github.com/revng/revng.git
clone_or_update resym             https://github.com/lt-asset/resym.git
clone_or_update rmux              https://github.com/Helvesec/rmux

# ── Cross-ISA Emulation ──────────────────────────────────────────────────────
clone_or_update FEX               https://github.com/FEX-Emu/FEX.git
clone_or_update box64             https://github.com/ptitSeb/box64.git

# ── AI Agents / Frameworks ───────────────────────────────────────────────────
clone_or_update OpenHands         https://github.com/All-Hands-AI/OpenHands.git
clone_or_update hermes-agent-self-evolution https://github.com/NousResearch/hermes-agent-self-evolution
clone_or_update CoEvoSkills       https://github.com/Zhang-Henry/CoEvoSkills.git
clone_or_update SkillGen          https://github.com/yccm/SkillGen.git
clone_or_update SkillX            https://github.com/zjunlp/SkillX.git
clone_or_update continual-harness https://github.com/sethkarten/continual-harness
clone_or_update elephant-agent   https://github.com/agentic-in/elephant-agent
clone_or_update agent-oss         https://github.com/quarqlabs/agent-oss
clone_or_update claude-p          https://github.com/smithersai/claude-p
clone_or_update CodexSaver        https://github.com/fendouai/CodexSaver
clone_or_update ShadowCat         https://github.com/unprovable/ShadowCat
clone_or_update piia-engram       https://github.com/Patdolitse/piia-engram
clone_or_update Photo-agents      https://github.com/jmerelnyc/Photo-agents
clone_or_update agency-swarm      https://github.com/VRSEN/agency-swarm.git
clone_or_update OpenSwarm         https://github.com/VRSEN/OpenSwarm.git

# ── Memory / Context ─────────────────────────────────────────────────────────
clone_or_update MemOS             https://github.com/MemTensor/MemOS.git
clone_or_update ai-memory         https://github.com/akitaonrails/ai-memory
clone_or_update DeepCode          https://github.com/HKUDS/DeepCode.git

# ── MCP / API Integration ────────────────────────────────────────────────────
clone_or_update jcodemunch-mcp    https://github.com/jgravelle/jcodemunch-mcp
clone_or_update fastmcp           https://github.com/jlowin/fastmcp.git
clone_or_update fastapi_mcp       https://github.com/tadata-org/fastapi_mcp.git
clone_or_update openapi-mcp-codegen https://github.com/cnoe-io/openapi-mcp-codegen.git
clone_or_update files-sdk         https://github.com/haydenbleasel/files-sdk

# ── Code Analysis / Intelligence ─────────────────────────────────────────────
clone_or_update paper2code        https://github.com/PrathamLearnsToCode/paper2code
clone_or_update codegraph         https://github.com/colbymchenry/codegraph
clone_or_update codeindex         https://github.com/scheidydude/codeindex
clone_or_update repomix           https://github.com/yamadashy/repomix.git
clone_or_update gitingest         https://github.com/coderamp-labs/gitingest.git
clone_or_update smallcode         https://github.com/Doorman11991/smallcode
clone_or_update auto-identity-remove https://github.com/stephenlthorn/auto-identity-remove

# ── Security / Offensive Research ────────────────────────────────────────────
clone_or_update LUKSbox           https://github.com/PentHertz/LUKSbox
clone_or_update opensquilla       https://github.com/OpenSquilla/opensquilla

# ── Runtime / Language Runtimes ──────────────────────────────────────────────
clone_or_update zerolang          https://github.com/vercel-labs/zerolang
clone_or_update zerostack         https://github.com/gi-dellav/zerostack
clone_or_update btype             https://github.com/tidwall/btype
clone_or_update chorus            https://github.com/chorus-codes/chorus

# ── Developer Tools ───────────────────────────────────────────────────────────
clone_or_update agent-rules-books https://github.com/ciembor/agent-rules-books.git
clone_or_update WSL               https://github.com/microsoft/WSL.git
clone_or_update auth.md           https://github.com/workos/auth.md

log ""
log "Done. $(ls "$TOOLS_DIR" | wc -l) tools present in $TOOLS_DIR"
log "See CREDITS.md for license information for each tool."
