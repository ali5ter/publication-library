#!/usr/bin/env bash
# bootstrap.sh — Full reconstruction pipeline for a publication-library instance.
#
# Reconstructs the complete library from a clean clone:
#   1. Validates configuration (.env, LIBRARY_BASE)
#   2. Creates cloud-storage directories for each collection
#   3. Runs init-symlinks.sh to restore local symlinks
#   4. Downloads PDFs for each collection (skips if already present)
#   5. Converts PDFs to searchable Markdown (skips if already done)
#   6. Regenerates the cross-collection CATALOGUE.md
#
# Name:         bootstrap.sh
# Description:  Full reconstruction pipeline for a publication-library instance
# Author:       Alister Lewis-Bowen <alister@lewis-bowen.org>
# Usage:        ./bootstrap.sh
# Dependencies: bash 4+, python3, pymupdf, git, pfb
# Exit codes:   0 success, 1 error
#
# Configuration (via .env or environment):
#   LIBRARY_BASE  Absolute path to the root of your cloud-synced library storage.
#                 See .env.template for examples.

set -euo pipefail

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Source .env if present
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

pfb heading "publication-library bootstrap" "📚"
echo

if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
    pfb error ".env not found."
    pfb subheading "Copy .env.template to .env and set LIBRARY_BASE:"
    pfb subheading "  cp .env.template .env"
    exit 1
fi

if [[ -z "${LIBRARY_BASE:-}" ]]; then
    pfb error "LIBRARY_BASE is not set in .env."
    pfb subheading "Edit .env and set LIBRARY_BASE to your cloud storage root."
    exit 1
fi

pfb info "LIBRARY_BASE: ${LIBRARY_BASE}"
echo

# ---------------------------------------------------------------------------
# Helper: parse Source URL from a COLLECTION.md
# @param $1  Path to COLLECTION.md
# @return    Prints the source URL, or empty string if not found
# ---------------------------------------------------------------------------
parse_source_url() {
    local col_md="${1}"
    [[ -f "${col_md}" ]] || { echo ""; return; }
    # Match:  | **Source** | [text](URL) |
    local url
    url="$(grep -oP '\|\s+\*\*Source\*\*\s+\|\s+\[[^\]]+\]\(\K[^)]+' "${col_md}" || true)"
    echo "${url}"
}

# ---------------------------------------------------------------------------
# Phase 1 — Create cloud-storage directories
# ---------------------------------------------------------------------------

pfb heading "Creating cloud-storage directories" "☁️"
echo

mkdir -p "${LIBRARY_BASE}/findings"
pfb success "READY  ${LIBRARY_BASE}/findings"

for col_dir in "${SCRIPT_DIR}/collections"/*/; do
    [[ -d "${col_dir}" ]] || continue
    name="$(basename "${col_dir}")"
    mkdir -p "${LIBRARY_BASE}/collections/${name}/pdfs"
    pfb success "READY  ${LIBRARY_BASE}/collections/${name}/pdfs"
    mkdir -p "${LIBRARY_BASE}/collections/${name}/indexed"
    pfb success "READY  ${LIBRARY_BASE}/collections/${name}/indexed"
done

echo

# ---------------------------------------------------------------------------
# Phase 2 — Restore symlinks
# ---------------------------------------------------------------------------

pfb heading "Restoring symlinks" "🔗"
echo
"${SCRIPT_DIR}/init-symlinks.sh"
echo

# ---------------------------------------------------------------------------
# Phase 3 — Download PDFs
# ---------------------------------------------------------------------------

pfb heading "Downloading PDFs" "⬇️"
echo

for col_dir in "${SCRIPT_DIR}/collections"/*/; do
    [[ -d "${col_dir}" ]] || continue
    name="$(basename "${col_dir}")"
    col_md="${col_dir}COLLECTION.md"

    source_url="$(parse_source_url "${col_md}")"

    if [[ -z "${source_url}" ]]; then
        pfb warn "SKIP  ${name} — no Source URL in COLLECTION.md"
        continue
    fi

    # Count PDFs already present (follow symlinks)
    pdf_count="$(find -L "${col_dir}pdfs" -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "${pdf_count}" -gt 0 ]]; then
        pfb info "SKIP  ${name} — ${pdf_count} PDFs already present"
        continue
    fi

    pfb subheading "${name} — downloading from ${source_url}"
    python3 "${SCRIPT_DIR}/download.py" "${source_url}" \
        --output-dir "collections/${name}/pdfs"
    pfb success "DONE  ${name}"
done

echo

# ---------------------------------------------------------------------------
# Phase 4 — Convert PDFs to Markdown
# ---------------------------------------------------------------------------

pfb heading "Converting PDFs to Markdown" "📄"
echo

for col_dir in "${SCRIPT_DIR}/collections"/*/; do
    [[ -d "${col_dir}" ]] || continue
    name="$(basename "${col_dir}")"

    # Skip if indexed output already exists and is non-empty
    indexed_count="$(find -L "${col_dir}indexed" -name "index.md" 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "${indexed_count}" -gt 0 ]]; then
        pfb info "SKIP  ${name} — already converted (${indexed_count} index files)"
        continue
    fi

    # Skip if there are no PDFs to convert
    pdf_count="$(find -L "${col_dir}pdfs" -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "${pdf_count}" -eq 0 ]]; then
        pfb warn "SKIP  ${name} — no PDFs found in collections/${name}/pdfs"
        continue
    fi

    pfb subheading "${name} — converting ${pdf_count} PDFs"
    python3 "${SCRIPT_DIR}/convert.py" \
        --input-dir "collections/${name}/pdfs" \
        --output-dir "collections/${name}/indexed" \
        --pattern "**/*.pdf" \
        --write-collection-md
    pfb success "DONE  ${name}"
done

echo

# ---------------------------------------------------------------------------
# Phase 5 — Regenerate catalogue
# ---------------------------------------------------------------------------

pfb heading "Regenerating CATALOGUE.md" "🗂️"
echo
python3 "${SCRIPT_DIR}/convert.py" --global-index collections/
echo
pfb success "Done. Library reconstruction complete."
