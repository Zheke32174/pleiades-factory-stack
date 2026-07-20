#!/usr/bin/env bash
# Compatibility entrypoint for the manifest-driven Pleiades Factory toolchain.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK="$ROOT/catalog/tools.lock.json"
command -v python3 >/dev/null 2>&1 || {
    echo "bootstrap-tools: python3 is required" >&2
    exit 1
}

# A fresh checkout deliberately carries no unreviewed floating lock. With no
# arguments, show the bounded core plan and the exact review step instead of
# failing or silently resolving mutable upstream heads.
if [[ $# -eq 0 && ! -f "$LOCK" ]]; then
    echo "bootstrap-tools: no reviewed lock is present; showing the non-mutating core plan." >&2
    python3 "$ROOT/scripts/toolchain.py" plan
    echo "bootstrap-tools: create and review one with:" >&2
    echo "  python3 scripts/toolchain.py lock --profile core" >&2
    echo "then rerun bash bootstrap-tools.sh for the locked sync." >&2
    exit 0
fi

# Historical compatibility:
#   bootstrap-tools.sh            -> sync core profile when a reviewed lock exists
#   bootstrap-tools.sh --update   -> re-apply the selected locked commits
# All other arguments are passed to `toolchain.py sync`.
args=(sync)
if [[ "${1:-}" == "--update" ]]; then
    args+=(--update)
    shift
fi
args+=("$@")

exec python3 "$ROOT/scripts/toolchain.py" "${args[@]}"
