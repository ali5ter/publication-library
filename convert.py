#!/usr/bin/env python3
"""
Convert magazine/book PDFs from World Radio History (or similar archives) to
searchable Markdown with rendered page images.

Extracts OCR text and renders each page as a PNG, producing per-publication
markdown files that embed page images alongside the extracted text. A master
index links all publications.

Usage:
    # Probe a directory to understand PDF structure before converting
    python3 convert.py --analyze [--input-dir DIR]

    # Convert all PDFs in a directory
    python3 convert.py [--input-dir DIR] [--output-dir DIR] [--dpi DPI] [--force]

Args:
    --analyze     Probe PDFs and report structure without converting
    --input-dir   Directory containing PDFs (required)
    --output-dir  Output directory for markdown and images (default: ./converted)
    --pattern     Glob pattern to select PDFs (default: **/*.pdf)
    --dpi         Render resolution for page images (default: 200)
    --force       Re-process publications even if output already exists
"""

import argparse
import re
import sys
from pathlib import Path
from collections import Counter

try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip3 install pymupdf")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Filename pattern detection
# ---------------------------------------------------------------------------

# Patterns tried in order; first match wins
_SLUG_PATTERNS: list[tuple[str, re.Pattern]] = [
    # PublicationName-YYYY-MM[...].pdf  →  YYYY-MM
    ("year-month", re.compile(r".*?[_-](\d{4})[_-](\d{2})(?:[_-]|\.|$)", re.IGNORECASE)),
    # Vol-N or V-N  →  vol-N
    ("volume", re.compile(r"(?:Vol(?:ume)?|V)[_\-\.\s]?(\d+)", re.IGNORECASE)),
    # No-N or Issue-N  →  no-N
    ("issue", re.compile(r"(?:No|Issue|Iss)[_\-\.\s]?(\d+)", re.IGNORECASE)),
    # Bare number anywhere in filename  →  NNN
    ("number", re.compile(r"(\d{2,4})")),
]

MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}


def parse_slug(filename: str) -> tuple[str, str]:
    """Derive a filesystem-safe slug and human title fragment from a filename.

    Tries date, volume, issue, and bare-number patterns in order, falling back
    to a cleaned version of the filename stem.

    @param filename: PDF filename (basename only)
    @return: (slug, label) e.g. ("1979-01", "January 1979") or ("vol-3", "Vol. 3")
    @example:
        parse_slug("Hobby-Electronics-1979-01-S-OCR.pdf")  # ("1979-01", "January 1979")
        parse_slug("Bernards-Babani-BP042.pdf")             # ("BP042", "BP042")
    """
    stem = Path(filename).stem

    for pattern_type, rx in _SLUG_PATTERNS:
        m = rx.search(stem)
        if not m:
            continue

        if pattern_type == "year-month":
            year, month = m.group(1), m.group(2)
            month_name = MONTH_NAMES.get(month, month)
            return f"{year}-{month}", f"{month_name} {year}"

        if pattern_type == "volume":
            n = m.group(1)
            return f"vol-{n}", f"Vol. {n}"

        if pattern_type == "issue":
            n = m.group(1)
            return f"no-{n}", f"No. {n}"

        if pattern_type == "number":
            n = m.group(1)
            return n, n

    # Fallback: sanitise the stem
    slug = re.sub(r"[^\w\-]", "-", stem).strip("-").lower()
    slug = re.sub(r"-{2,}", "-", slug)
    return slug, stem


def resolve_slugs(pdfs: list[Path]) -> dict[Path, str]:
    """Build a path-to-slug mapping, disambiguating any collisions.

    When multiple PDFs resolve to the same slug, appends the parent directory
    name to each slug to make them unique.

    @param pdfs: List of PDF paths to map
    @return: Dict mapping each PDF path to its unique slug
    @example:
        # 70s/ETI-1985-08.pdf and 80s/ETI-1985-08.pdf both parse to "1985-08"
        # resolve_slugs returns {70s/...: "1985-08-70s", 80s/...: "1985-08-80s"}
    """
    slug_to_paths: dict[str, list[Path]] = {}
    for pdf_path in pdfs:
        base_slug, _ = parse_slug(pdf_path.name)
        slug_to_paths.setdefault(base_slug, []).append(pdf_path)

    result: dict[Path, str] = {}
    collision_found = False
    for base_slug, paths in slug_to_paths.items():
        if len(paths) == 1:
            result[paths[0]] = base_slug
        else:
            if not collision_found:
                print("WARNING: Slug collisions detected — disambiguating with parent directory name:")
                collision_found = True
            for path in sorted(paths):
                disambig = f"{base_slug}-{path.parent.name}"
                result[path] = disambig
                print(f"  {path.name} → {disambig}")
    if collision_found:
        print()
    return result


def infer_publication_name(stem: str) -> str:
    """Extract a likely publication name from a filename stem.

    Strips trailing date/number/OCR artefacts, converts hyphens to spaces.

    @param stem: Filename without extension
    @return: Human-readable publication name guess
    @example:
        infer_publication_name("Hobby-Electronics-1979-01-S-OCR")  # "Hobby Electronics"
        infer_publication_name("Practical-Wireless-1965-03")       # "Practical Wireless"
    """
    # Remove common suffixes: S-OCR, OCR, Vol-N, YYYY-MM, numbers
    cleaned = re.sub(
        r"[_\-]?(S[_\-]?OCR|OCR|Vol[_\-]\d+|No[_\-]\d+|\d{4}[_\-]\d{2}|\d+).*$",
        "", stem, flags=re.IGNORECASE,
    )
    return re.sub(r"[_\-]+", " ", cleaned).strip()


# ---------------------------------------------------------------------------
# PDF analysis
# ---------------------------------------------------------------------------

def probe_pdf(pdf_path: Path) -> dict:
    """Gather structural information about a PDF without converting it.

    @param pdf_path: Path to the PDF file
    @return: Dict with keys: filename, pages, has_text, image_pages, text_sample, slug, label
    """
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        return {"filename": pdf_path.name, "error": str(e)}

    num_pages = len(doc)
    text_pages = 0
    image_pages = 0
    text_sample = ""

    for i in range(min(num_pages, 10)):
        page = doc[i]
        text = page.get_text().strip()
        if text:
            text_pages += 1
            if not text_sample:
                text_sample = text[:120].replace("\n", " ")
        imgs = page.get_images()
        if imgs:
            image_pages += 1

    doc.close()
    slug, label = parse_slug(pdf_path.name)
    pub_name = infer_publication_name(pdf_path.stem)

    return {
        "filename": pdf_path.name,
        "slug": slug,
        "label": label,
        "pub_name": pub_name,
        "pages": num_pages,
        "has_text": text_pages > 0,
        "text_pages_sampled": text_pages,
        "image_pages_sampled": image_pages,
        "text_sample": text_sample,
    }


def analyze_directory(input_dir: Path, pattern: str) -> None:
    """Print a structural report for all PDFs in a directory.

    @param input_dir: Directory to scan
    @param pattern: Glob pattern to filter files
    """
    pdfs = sorted(input_dir.glob(pattern))
    if not pdfs:
        print(f"No files matching '{pattern}' found in {input_dir}")
        return

    print(f"Analyzing {len(pdfs)} PDFs in {input_dir} ...\n")

    pub_names: Counter = Counter()
    slug_types: Counter = Counter()
    probes = []

    for pdf_path in pdfs:
        info = probe_pdf(pdf_path)
        probes.append(info)
        if "error" not in info:
            pub_names[info["pub_name"]] += 1
            # Detect slug type used
            for pt, rx in _SLUG_PATTERNS:
                if rx.search(pdf_path.stem):
                    slug_types[pt] += 1
                    break
            else:
                slug_types["filename-stem"] += 1

    # Summary
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"  Total PDFs      : {len(pdfs)}")
    print(f"  Detected titles : {dict(pub_names.most_common(5))}")
    print(f"  Slug patterns   : {dict(slug_types)}")
    print()

    # Per-file table
    print(f"{'FILENAME':<50} {'SLUG':<16} {'PGS':>4} {'TEXT':>5} {'IMGS':>5}")
    print("-" * 84)
    for info in probes:
        if "error" in info:
            print(f"  ERROR: {info['filename']}: {info['error']}")
            continue
        has_text = "yes" if info["has_text"] else "NO"
        imgs = info["image_pages_sampled"]
        print(
            f"  {info['filename']:<48} {info['slug']:<16} "
            f"{info['pages']:>4} {has_text:>5} {imgs:>5}"
        )

    print()
    print("Sample text from first PDF with OCR:")
    for info in probes:
        if info.get("text_sample"):
            print(f"  [{info['filename']}]")
            print(f"  {info['text_sample']}")
            break

    print()
    print("Suggested convert command:")
    print(f"  python3 convert.py --input-dir \"{input_dir}\" --output-dir converted/")


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Normalise OCR text for markdown output.

    @param text: Raw OCR text from a PDF page
    @return: Cleaned text suitable for markdown
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def render_page_png(page: fitz.Page, output_path: Path, dpi: int) -> None:
    """Render a PDF page to a PNG file.

    @param page: PyMuPDF page object
    @param output_path: Destination PNG path
    @param dpi: Render resolution in dots per inch
    """
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pixmap = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB)
    pixmap.save(str(output_path))


def convert_publication(pdf_path: Path, output_dir: Path, dpi: int, force: bool, slug_override: str | None = None) -> dict:
    """Convert a single PDF to markdown with rendered page images.

    @param pdf_path: Path to the source PDF
    @param output_dir: Root output directory
    @param dpi: Page render resolution
    @param force: Re-process even if output exists
    @param slug_override: Optional pre-resolved slug (used when collision disambiguation is applied)
    @return: Dict with slug, title, pages, articles for index building
    """
    slug, label = parse_slug(pdf_path.name)
    if slug_override is not None:
        slug = slug_override
    pub_name = infer_publication_name(pdf_path.stem)
    title = f"{pub_name} — {label}"

    pub_dir = output_dir / slug
    pages_dir = pub_dir / "pages"
    content_path = pub_dir / "content.md"

    if content_path.exists() and not force:
        print(f"  SKIP (already converted): {slug}")
        return {"slug": slug, "title": title, "articles": [], "pages": 0}

    pub_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(exist_ok=True)

    doc = fitz.open(str(pdf_path))
    num_pages = len(doc)
    print(f"  Converting {slug} ({num_pages} pages) ...")

    md_lines = [
        f"# {title}",
        "",
        f"**Source:** `{pdf_path.name}`  ",
        f"**Pages:** {num_pages}",
        "",
        "---",
        "",
    ]

    articles = []

    for page_num in range(num_pages):
        page = doc[page_num]
        png_filename = f"page-{page_num + 1:03d}.png"
        png_path = pages_dir / png_filename

        if not png_path.exists() or force:
            render_page_png(page, png_path, dpi)

        text = clean_text(page.get_text())

        first_line = text.splitlines()[0].strip() if text else ""
        if first_line and 4 < len(first_line) < 60:
            articles.append((page_num + 1, first_line))

        md_lines.append(f"## Page {page_num + 1}")
        md_lines.append("")
        md_lines.append(f"![Page {page_num + 1}](pages/{png_filename})")
        md_lines.append("")

        if text:
            md_lines.append("### Extracted Text")
            md_lines.append("")
            md_lines.append(text)
            md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    doc.close()

    with open(content_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return {"slug": slug, "title": title, "articles": articles, "pages": num_pages}


def write_publication_index(info: dict, output_dir: Path) -> None:
    """Write a concise index.md for a single publication.

    @param info: Dict from convert_publication()
    @param output_dir: Root output directory
    """
    pub_dir = output_dir / info["slug"]
    lines = [
        f"# {info['title']}",
        "",
        "[Full content with page images](content.md)",
        "",
        "## Detected Articles / Sections",
        "",
    ]
    for page_num, heading in info.get("articles", []):
        lines.append(f"- **p.{page_num}** — {heading}")
    lines.append("")

    with open(pub_dir / "index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_master_index(all_publications: list[dict], output_dir: Path) -> None:
    """Write the master index.md linking all converted publications.

    @param all_publications: List of info dicts from convert_publication()
    @param output_dir: Root output directory
    """
    lines = [
        "# Magazine / Book Archive",
        "",
        "Converted from PDF for full-text search and AI-assisted content discovery.",
        "",
        "## Publications",
        "",
        "| Title | Pages | Links |",
        "|-------|-------|-------|",
    ]

    for pub in sorted(all_publications, key=lambda x: x.get("slug", "")):
        if not pub.get("slug"):
            continue
        slug = pub["slug"]
        lines.append(
            f"| {pub['title']} | {pub.get('pages', '?')} | "
            f"[content]({slug}/content.md) · [index]({slug}/index.md) |"
        )

    lines += [
        "",
        "## Searching",
        "",
        "```bash",
        "# Case-insensitive search across all issues",
        'grep -ril "search term" converted/',
        "",
        "# Show matching lines with context",
        'grep -in -A2 "VCA" converted/*/content.md',
        "",
        "# Find circuit projects (pages with a Fig. 1 schematic)",
        'grep -il "Fig. 1" converted/*/content.md',
        "```",
        "",
    ]

    with open(output_dir / "index.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert archive PDFs (magazines, books) to searchable Markdown"
    )
    parser.add_argument("--analyze", action="store_true", help="Probe PDFs and report structure without converting")
    parser.add_argument("--input-dir", type=Path, required=True, help="Source PDF directory")
    parser.add_argument("--output-dir", type=Path, default=Path("converted"), help="Output directory (default: ./converted)")
    parser.add_argument("--pattern", default="**/*.pdf", help="Glob pattern to select PDFs (default: **/*.pdf)")
    parser.add_argument("--dpi", type=int, default=200, help="Page image render DPI (default: 200)")
    parser.add_argument("--force", action="store_true", help="Re-process already-converted publications")
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"ERROR: Input directory not found: {args.input_dir}")
        sys.exit(1)

    if args.analyze:
        analyze_directory(args.input_dir, args.pattern)
        return

    pdfs = sorted(args.input_dir.glob(args.pattern))
    if not pdfs:
        print(f"No PDFs found matching '{args.pattern}' in {args.input_dir}")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(pdfs)} PDFs in {args.input_dir}")
    print(f"Output: {args.output_dir}  |  DPI: {args.dpi}")
    print()

    slug_map = resolve_slugs(pdfs)

    all_pubs = []
    for i, pdf_path in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] {pdf_path.name}")
        base_slug, _ = parse_slug(pdf_path.name)
        resolved = slug_map[pdf_path]
        override = resolved if resolved != base_slug else None
        info = convert_publication(pdf_path, args.output_dir, args.dpi, args.force, slug_override=override)
        if info.get("slug"):
            write_publication_index(info, args.output_dir)
            all_pubs.append(info)

    print()
    print("Writing master index ...")
    write_master_index(all_pubs, args.output_dir)

    total_pages = sum(p.get("pages", 0) for p in all_pubs)
    print(f"Done. {len(all_pubs)} publications, {total_pages} pages total.")
    print(f"Master index: {args.output_dir}/index.md")


if __name__ == "__main__":
    main()
