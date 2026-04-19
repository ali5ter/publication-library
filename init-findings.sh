#!/usr/bin/env bash
# init-findings.sh — Scaffold the findings/ directory for research outputs.
#
# Creates the recommended directory structure under findings/ and optionally
# sets up a symlink to a cloud storage location (Dropbox, iCloud, Google Drive).
#
# Name:         init-findings.sh
# Description:  Scaffold findings/ directory for publication-library research
# Author:       Alister Lewis-Bowen <alister@lewis-bowen.org>
# Usage:        ./init-findings.sh [--cloud dropbox|icloud|gdrive|local]
# Dependencies: bash 4+
# Exit codes:   0 success, 1 error

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FINDINGS_DIR="${SCRIPT_DIR}/findings"
CLOUD_TYPE="${1:-}"

# Load pfb for terminal output
PFB_SCRIPT="${SCRIPT_DIR}/lib/pfb/pfb.sh"
if [[ -f "${PFB_SCRIPT}" ]]; then
    # shellcheck source=lib/pfb/pfb.sh
    source "${PFB_SCRIPT}"
elif command -v pfb &>/dev/null; then
    : # pfb already on PATH
else
    echo "ERROR: pfb not found. Run: git submodule update --init lib/pfb" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# @description Print a usage message and exit
usage() {
    echo "Usage: $0 [--cloud dropbox|icloud|gdrive|local]"
    echo
    echo "  --cloud   Set up a symlink to cloud storage (optional)"
    echo
    echo "Examples:"
    echo "  $0                   # Create findings/ locally"
    echo "  $0 --cloud dropbox   # Symlink findings/ to Dropbox"
    exit 1
}

# @description Resolve the cloud storage path for a given provider
# @param $1 Cloud provider: dropbox, icloud, gdrive, or local
# @return Prints the resolved path, or exits 1 if unknown
cloud_path() {
    local provider="${1}"
    local lib_name
    lib_name="$(basename "${SCRIPT_DIR}")"

    case "${provider}" in
        dropbox)
            echo "${HOME}/Dropbox/${lib_name}/findings"
            ;;
        icloud)
            echo "${HOME}/Library/Mobile Documents/com~apple~CloudDocs/${lib_name}/findings"
            ;;
        gdrive)
            echo "${HOME}/Google Drive/My Drive/${lib_name}/findings"
            ;;
        local)
            echo "${FINDINGS_DIR}"
            ;;
        *)
            echo "ERROR: Unknown cloud provider '${provider}'. Use: dropbox, icloud, gdrive, local" >&2
            exit 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# Parse arguments
CLOUD=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cloud)
            CLOUD="${2:-}"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "ERROR: Unknown argument '$1'" >&2
            usage
            ;;
    esac
done

pfb heading "publication-library — findings/ setup" "📁"
echo

# Determine where findings will live
if [[ -n "${CLOUD}" ]]; then
    CLOUD_DEST="$(cloud_path "${CLOUD}")"
    pfb info "Cloud storage: ${CLOUD} → ${CLOUD_DEST}"

    # Create the cloud directory and scaffold inside it
    mkdir -p "${CLOUD_DEST}/topics"
    mkdir -p "${CLOUD_DEST}/projects"
    mkdir -p "${CLOUD_DEST}/sessions"

    # Create symlink if findings/ doesn't already exist
    if [[ -e "${FINDINGS_DIR}" ]]; then
        pfb info "${FINDINGS_DIR} already exists — skipping symlink"
    else
        ln -s "${CLOUD_DEST}" "${FINDINGS_DIR}"
        pfb success "Symlink created: ${FINDINGS_DIR} → ${CLOUD_DEST}"
    fi
else
    # Local only
    mkdir -p "${FINDINGS_DIR}/topics"
    mkdir -p "${FINDINGS_DIR}/projects"
    mkdir -p "${FINDINGS_DIR}/sessions"
    pfb success "Created: ${FINDINGS_DIR}/"
fi

echo
pfb subheading "findings/"
pfb subheading "  ├── topics/    — topic reference notes (e.g. synthesisers.md)"
pfb subheading "  ├── projects/  — project research notes"
pfb subheading "  └── sessions/  — dated session logs (YYYY-MM-DD-topic.md)"
echo
pfb success "Done. findings/ is gitignored and will not be committed."
