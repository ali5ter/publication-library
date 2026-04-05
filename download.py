#!/usr/bin/env python3
"""
Download all magazine PDFs from a World Radio History archive page.

Fetches the given page, extracts all PDF links, and downloads them into a
local directory — preserving the remote subdirectory structure so issues and
special collections land in separate folders. Already-downloaded files are
skipped, making the script safe to re-run.

Usage:
    python3 download.py <url> [--output-dir DIR] [--delay SECONDS] [--dry-run]

Args:
    url           World Radio History page URL to scrape PDF links from
    --output-dir  Local directory to download into (default: ./Downloads/<hostname>)
    --delay       Seconds to wait between downloads (default: 2)
    --dry-run     List what would be downloaded without downloading anything
    --filter      Only download URLs containing this string (e.g. "1979")

Examples:
    python3 download.py https://www.worldradiohistory.com/ETI_Magazine.htm
    python3 download.py https://www.worldradiohistory.com/ETI_Magazine.htm --dry-run
    python3 download.py https://www.worldradiohistory.com/ETI_Magazine.htm --filter "UK/Electronics-Today-UK"
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
    # Strip leading slash from path
    rel_path = parsed.path.lstrip("/")
    # URL-decode the path (handles %20 etc.)
    rel_path = urllib.parse.unquote(rel_path)
    return output_dir / rel_path


def download_file(url: str, dest: Path) -> bool:
    """Download a single file, returning True on success.

    @param url: URL to download
    @param dest: Local destination path
    @return: True if downloaded, False if skipped (already exists)
    """
    if dest.exists():
        return False  # Already downloaded

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download PDFs from a World Radio History archive page"
    )
    parser.add_argument("url", help="Archive page URL")
    parser.add_argument("--output-dir", type=Path, help="Download root directory (default: ./Downloads)")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between downloads (default: 2)")
    parser.add_argument("--dry-run", action="store_true", help="List files without downloading")
    parser.add_argument("--filter", help="Only download URLs containing this string")
    args = parser.parse_args()

    parsed_url = urllib.parse.urlparse(args.url)
    if not args.output_dir:
        args.output_dir = Path("Downloads") / parsed_url.hostname

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


if __name__ == "__main__":
    main()
