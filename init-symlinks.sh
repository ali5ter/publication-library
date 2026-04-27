#!/usr/bin/env bash
# init-symlinks.sh — Recreate cloud-storage symlinks for a publication-library instance.
#
# All PDFs, indexed output, and findings are stored in a cloud-synced directory
# (Dropbox, iCloud, Google Drive, etc.) and linked into the project directory.
# Run this script after cloning or on a new machine to restore those links.
#
# Name:         init-symlinks.sh
# Description:  Recreate cloud-storage symlinks for a publication-library instance
# Author:       Alister Lewis-Bowen <alister@lewis-bowen.org>
# Usage:        ./init-symlinks.sh
# Dependencies: bash 4+, pfb
# Exit codes:   0 success, 1 error
#
# Configuration (via .env or environment):
#   LIBRARY_BASE  Absolute path to the root of your cloud-synced library storage.
#                 See .env.template for examples.
#
# LINKS are auto-derived from collections/*/ using the naming convention:
#   collections/NAME/pdfs    → ${LIBRARY_BASE}/collections/NAME/pdfs
#   collections/NAME/indexed → ${LIBRARY_BASE}/collections/NAME/indexed
#   findings                 → ${LIBRARY_BASE}/findings
#
# To override, define a LINKS array in .env before running:
#   LINKS=(
#     "findings:${LIBRARY_BASE}/findings"
#     "collections/NAME/pdfs:${LIBRARY_BASE}/collections/NAME/pdfs"
#     "collections/NAME/indexed:${LIBRARY_BASE}/collections/NAME/indexed"
#   )

set -euo pipefail

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Source .env if present (allows LIBRARY_BASE and optional LINKS override to be set there)
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
    # shellcheck source=/dev/null
    source "${SCRIPT_DIR}/.env"
fi

# Require pfb for terminal output
if ! command -v pfb &>/dev/null; then
    echo "ERROR: pfb is required but not found. Install it from https://github.com/ali5ter/pfb" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate required configuration
# ---------------------------------------------------------------------------

if [[ -z "${LIBRARY_BASE:-}" ]]; then
    pfb error "LIBRARY_BASE is not set."
    echo
    pfb subheading "Set it in .env (copy .env.template) or export it before running:"
    pfb subheading "  export LIBRARY_BASE=\"/path/to/your/cloud/library\""
    exit 1
fi

# ---------------------------------------------------------------------------
# Build LINKS — auto-derive from collections/*/ unless overridden in .env
# ---------------------------------------------------------------------------

# @description Build the LINKS array from collections/*/ directories.
# @side_effects Populates the global LINKS array.
build_links() {
    LINKS=()
    LINKS+=("findings:${LIBRARY_BASE}/findings")
    for col_dir in "${SCRIPT_DIR}/collections"/*/; do
        [[ -d "${col_dir}" ]] || continue
        name="$(basename "${col_dir}")"
        LINKS+=("collections/${name}/pdfs:${LIBRARY_BASE}/collections/${name}/pdfs")
        LINKS+=("collections/${name}/indexed:${LIBRARY_BASE}/collections/${name}/indexed")
    done
}

if [[ -z "${LINKS[*]+set}" ]] || [[ ${#LINKS[@]} -eq 0 ]]; then
    build_links
fi

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

pfb heading "Recreating cloud-storage symlinks" "🔗"
pfb subheading "LIBRARY_BASE: ${LIBRARY_BASE}"
echo

if [[ ${#LINKS[@]} -eq 0 ]]; then
    pfb warn "No collections found under collections/ and no LINKS defined in .env."
    exit 0
fi

linked=0
skipped=0
missing=0

for entry in "${LINKS[@]}"; do
    local_path="${entry%%:*}"
    target="${entry##*:}"

    if [[ -L "${local_path}" ]]; then
        pfb info "EXISTS   ${local_path}"
        (( skipped++ )) || true
        continue
    fi

    if [[ ! -e "${target}" ]]; then
        pfb warn "SKIP     ${local_path} (target not found: ${target})"
        (( missing++ )) || true
        continue
    fi

    parent_dir="$(dirname "${local_path}")"
    mkdir -p "${parent_dir}"
    ln -s "${target}" "${local_path}"
    pfb success "LINKED   ${local_path} → ${target}"
    (( linked++ )) || true
done

echo
pfb subheading "Linked: ${linked}  |  Already existed: ${skipped}  |  Target not found: ${missing}"
echo
pfb success "Done."
