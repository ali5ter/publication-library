#!/usr/bin/env python3
"""
Download magazine PDFs from a World Radio History archive page or an archive.org item.

Source is auto-detected from the URL:
  - archive.org/details/... → archive.org item download (requires internetarchive)
  - all other URLs          → World Radio History link-scrape mode

Usage:
    python3 download.py <url> [--output-dir DIR] [--delay SECONDS] [--dry-run]
                              [--filter STRING]
                              [--pdf-format {text,image,both}]
                              [--year-from YEAR] [--year-to YEAR]

Args:
    url               Archive page URL or archive.org item URL
    --output-dir      Local directory to download into (default: ./Downloads/<hostname>)
    --delay           Seconds to wait between downloads (default: 2)
    --dry-run         List what would be downloaded without downloading anything
    --filter          Only download URLs/filenames containing this string (WRH mode only)
    --pdf-format      Which PDF variant to download from archive.org:
                        text  → *_text.pdf only — Abbyy OCR overlay (default)
                        image → plain *.pdf only — image container, may lack OCR
                        both  → download both variants
    --year-from       Only download files whose filename contains a year >= this value
    --year-to         Only download files whose filename contains a year <= this value

Examples:
    # World Radio History
    python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm"
    python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" --dry-run
    python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" \\
        --filter "UK/Electronics-Today-UK"

    # archive.org
    python3 download.py "https://archive.org/details/ElektorMagazine" \\
        --output-dir collections/elektor/pdfs \\
        --year-from 1974 --year-to 1989
    python3 download.py "https://archive.org/details/ElektorMagazine" \\
        --pdf-format both --dry-run

Author: Alister Lewis-Bowen <alister@lewis-bowen.org>
"""

import argparse
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def download_file(url: str, dest: Path) -> bool:
    """Download a single file, returning True on success.

    @param url: URL to download
    @param dest: Local destination path
    @return: True if downloaded, False if skipped (already exists)
    """
    if dest.exists():
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)
        tmp.rename(dest)
        return True
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(f"Failed to download {url}: {e}") from e


def format_size(path: Path) -> str:
    """Format a file's size as a human-readable string.

    @param path: Path to an existing file
    @return: Human-readable size string, e.g. "4.2 MB"
    """
    size = path.stat().st_size
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def format_size_bytes(size_bytes: int | None) -> str:
    """Format a byte count as a human-readable string.

    @param size_bytes: File size in bytes, or None if unknown
    @return: Human-readable size string
    """
    if size_bytes is None:
        return "? B"
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def extract_year(filename: str) -> int | None:
    """Extract the first four-digit year from a filename.

    @param filename: File name to search
    @return: Year as int, or None if not found
    """
    m = re.search(r"(\d{4})", filename)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# World Radio History mode
# ---------------------------------------------------------------------------

def fetch_page(url: str) -> str:
    """Fetch a web page and return its HTML content.

    @param url: Page URL to fetch
    @return: HTML content as string
    """
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_pdf_links(html: str, base_url: str) -> list[str]:
    """Extract all PDF hrefs from a page and resolve them to absolute URLs.

    @param html: Raw HTML content
    @param base_url: Base URL of the page for resolving relative links
    @return: Sorted list of absolute PDF URLs
    """
    hrefs = re.findall(r'href="([^"]*\.pdf)"', html, re.IGNORECASE)
    absolute = set()
    for href in hrefs:
        full = urllib.parse.urljoin(base_url, href)
        parsed = urllib.parse.urlparse(full)
        encoded_path = urllib.parse.quote(parsed.path, safe="/:@!$&'()*+,;=")
        full = parsed._replace(path=encoded_path).geturl()
        absolute.add(full)
    return sorted(absolute)


def url_to_local_path(pdf_url: str, output_dir: Path, base_url: str) -> Path:
    """Convert a PDF URL to a local file path, preserving subdirectory structure.

    @param pdf_url: Absolute URL of the PDF
    @param output_dir: Root local download directory
    @param base_url: Base URL of the archive page (used to strip the hostname prefix)
    @return: Local Path where the file should be saved
    """
    parsed = urllib.parse.urlparse(pdf_url)
    rel_path = parsed.path.lstrip("/")
    rel_path = urllib.parse.unquote(rel_path)
    return output_dir / rel_path


def run_worldradiohistory(args: argparse.Namespace) -> None:
    """Download PDFs from a World Radio History archive page.

    @param args: Parsed command-line arguments
    """
    print(f"Fetching index: {args.url}")
    try:
        html = fetch_page(args.url)
    except Exception as e:
        print(f"ERROR fetching page: {e}")
        sys.exit(1)

    pdf_urls = extract_pdf_links(html, args.url)

    if args.filter:
        pdf_urls = [u for u in pdf_urls if args.filter in u]

    print(f"Found {len(pdf_urls)} PDFs")
    if args.filter:
        print(f"Filtered to {len(pdf_urls)} matching '{args.filter}'")
    print(f"Output directory: {args.output_dir}")
    print()

    if args.dry_run:
        print("DRY RUN — files that would be downloaded:")
        for url in pdf_urls:
            dest = url_to_local_path(url, args.output_dir, args.url)
            status = "EXISTS" if dest.exists() else "NEW"
            print(f"  [{status}] {dest}")
        return

    downloaded = 0
    skipped = 0
    errors = 0

    for i, url in enumerate(pdf_urls, 1):
        dest = url_to_local_path(url, args.output_dir, args.url)
        filename = dest.name

        try:
            did_download = download_file(url, dest)
            if did_download:
                size = format_size(dest)
                print(f"[{i}/{len(pdf_urls)}] {filename} ({size})")
                downloaded += 1
                time.sleep(args.delay)
            else:
                print(f"[{i}/{len(pdf_urls)}] SKIP {filename}")
                skipped += 1
        except RuntimeError as e:
            print(f"[{i}/{len(pdf_urls)}] ERROR: {e}")
            errors += 1

    print()
    print(f"Done. Downloaded: {downloaded}  Skipped: {skipped}  Errors: {errors}")
    print(f"Files saved to: {args.output_dir}")


# ---------------------------------------------------------------------------
# archive.org mode
# ---------------------------------------------------------------------------

def get_archive_org_item_id(url: str) -> str:
    """Extract the archive.org item identifier from a /details/ URL.

    @param url: archive.org URL containing /details/<identifier>
    @return: Item identifier string
    @example: "https://archive.org/details/ElektorMagazine" → "ElektorMagazine"
    """
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    try:
        idx = parts.index("details")
        return urllib.parse.unquote(parts[idx + 1])
    except (ValueError, IndexError):
        print(f"ERROR: Cannot extract item identifier from URL: {url}")
        sys.exit(1)


def select_archive_files(files: list, pdf_format: str, year_from: int | None, year_to: int | None) -> list:
    """Filter archive.org file list by PDF format and optional year range.

    @param files: List of internetarchive File objects
    @param pdf_format: One of "text", "image", or "both"
    @param year_from: Lower year bound (inclusive), or None
    @param year_to: Upper year bound (inclusive), or None
    @return: Filtered and sorted list of File objects
    """
    # Keep only PDFs
    selected = [f for f in files if f.name.lower().endswith(".pdf")]

    # Filter by format variant
    if pdf_format == "text":
        selected = [f for f in selected if f.name.lower().endswith("_text.pdf")]
    elif pdf_format == "image":
        selected = [f for f in selected if not f.name.lower().endswith("_text.pdf")]
    # "both" keeps all PDFs

    # Filter by year range
    if year_from is not None or year_to is not None:
        filtered = []
        for f in selected:
            year = extract_year(f.name)
            if year is None:
                filtered.append(f)  # no year in name — include by default
                continue
            if year_from is not None and year < year_from:
                continue
            if year_to is not None and year > year_to:
                continue
            filtered.append(f)
        selected = filtered

    return sorted(selected, key=lambda f: f.name)


def run_archive_org(args: argparse.Namespace) -> None:
    """Download PDFs from an archive.org item.

    @param args: Parsed command-line arguments
    """
    try:
        import internetarchive as ia
    except ImportError:
        print("ERROR: The 'internetarchive' package is required for archive.org downloads.")
        print("       Install it with: pip3 install internetarchive")
        sys.exit(1)

    item_id = get_archive_org_item_id(args.url)
    print(f"Fetching archive.org item: {item_id}")

    item = ia.get_item(item_id)
    all_files = list(item.get_files())

    selected = select_archive_files(
        all_files,
        pdf_format=args.pdf_format,
        year_from=args.year_from,
        year_to=args.year_to,
    )

    year_range = ""
    if args.year_from or args.year_to:
        lo = str(args.year_from) if args.year_from else "any"
        hi = str(args.year_to) if args.year_to else "any"
        year_range = f" (years {lo}–{hi})"

    print(f"Found {len(selected)} PDFs{year_range} [format: {args.pdf_format}]")
    print(f"Output directory: {args.output_dir}")
    print()

    if args.dry_run:
        print("DRY RUN — files that would be downloaded:")
        for f in selected:
            dest = args.output_dir / f.name
            status = "EXISTS" if dest.exists() else "NEW"
            size = format_size_bytes(f.size)
            print(f"  [{status}] {f.name} ({size})")
        return

    downloaded = 0
    skipped = 0
    errors = 0
    total = len(selected)

    for i, f in enumerate(selected, 1):
        dest = args.output_dir / f.name

        if dest.exists():
            print(f"[{i}/{total}] SKIP {f.name}")
            skipped += 1
            continue

        file_url = f"https://archive.org/download/{urllib.parse.quote(item_id)}/{urllib.parse.quote(f.name)}"

        try:
            download_file(file_url, dest)
            size = format_size(dest)
            print(f"[{i}/{total}] {f.name} ({size})")
            downloaded += 1
            time.sleep(args.delay)
        except RuntimeError as e:
            print(f"[{i}/{total}] ERROR: {e}")
            errors += 1

    print()
    print(f"Done. Downloaded: {downloaded}  Skipped: {skipped}  Errors: {errors}")
    print(f"Files saved to: {args.output_dir}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments, detect source, and dispatch to the appropriate downloader."""
    parser = argparse.ArgumentParser(
        description="Download PDFs from a World Radio History page or an archive.org item"
    )
    parser.add_argument("url", help="Archive page URL or archive.org item URL")
    parser.add_argument(
        "--output-dir", type=Path, help="Download root directory (default: ./Downloads/<hostname>)"
    )
    parser.add_argument(
        "--delay", type=float, default=2.0, help="Seconds between downloads (default: 2)"
    )
    parser.add_argument("--dry-run", action="store_true", help="List files without downloading")

    # World Radio History options
    parser.add_argument("--filter", help="Only download URLs containing this string (WRH mode only)")

    # archive.org options
    parser.add_argument(
        "--pdf-format",
        choices=["text", "image", "both"],
        default="text",
        help=(
            "Which PDF variant to download from archive.org: "
            "text=*_text.pdf (OCR, default), image=plain *.pdf, both=all variants"
        ),
    )
    parser.add_argument(
        "--year-from",
        type=int,
        metavar="YEAR",
        help="Only download files whose filename contains a year >= YEAR",
    )
    parser.add_argument(
        "--year-to",
        type=int,
        metavar="YEAR",
        help="Only download files whose filename contains a year <= YEAR",
    )

    args = parser.parse_args()

    parsed_url = urllib.parse.urlparse(args.url)
    if not args.output_dir:
        args.output_dir = Path("Downloads") / parsed_url.hostname

    if "archive.org/details/" in args.url:
        run_archive_org(args)
    else:
        run_worldradiohistory(args)


if __name__ == "__main__":
    main()
