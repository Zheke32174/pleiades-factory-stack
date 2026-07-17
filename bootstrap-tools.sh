#!/usr/bin/env bash
# Compatibility entrypoint for the manifest-driven Pleiades Factory toolchain.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || {
    echo "bootstrap-tools: python3 is required" >&2
    exit 1
}

# Historical compatibility:
#   bootstrap-tools.sh            -> sync core profile, locked only
#   bootstrap-tools.sh --update   -> sync core profile, update floating clones
# All other arguments are passed to `toolchain.py sync`.
args=(sync)
if [[ "${1:-}" == "--update" ]]; then
    args+=(--update)
    shift
fi
args+=("$@")

exec python3 "$ROOT/scripts/toolchain.py" "${args[@]}"
