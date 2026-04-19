#!/usr/bin/env python3
"""Search across indexed library collections and display formatted results.

Wraps grep to provide structured output grouped by publication. Results show
the collection name, publication slug, and matching lines with context.

Usage:
    python3 search.py TERM [options]

Args:
    term              Search term (case-insensitive)
    --collections-dir Root collections directory (default: ./collections)
    --collection      Limit search to one collection by directory name
    --context         Lines of context around each match (default: 1)
    --files-only      Show only matching publication slugs, not lines

Examples:
    python3 search.py "fuzz box"
    python3 search.py "VCA" --collection eti
    python3 search.py synthesiser --files-only
    python3 search.py "guitar" --context 3

Author: Alister Lewis-Bowen <alister@lewis-bowen.org>
Version: 1.0.0
Date: 2026-04-05
License: MIT
Dependencies: grep (system)
Exit codes:
    0: Success
    1: Error (collections directory not found, or no matches)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def search_indexed(term: str, indexed_dir: Path, context: int) -> list[dict]:
    """Search a collection's content.md files for a term.

    Args:
        term: Search term (case-insensitive).
        indexed_dir: Path to the collection's indexed directory.
        context: Lines of context around each match.

    Returns:
        List of dicts with keys: slug, line_num, content.
    """
    cmd = ["grep", "-rin", f"--include=content.md", f"-C{context}", term, str(indexed_dir) + "/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        print(f"  WARNING: grep error in {indexed_dir}: {result.stderr.strip()}", file=sys.stderr)
        return []

    matches: list[dict] = []
    for line in result.stdout.splitlines():
        # grep -C output uses "--" as separators between groups; skip them
        if line == "--":
            continue
        # Match lines in format: path:line_num:content  or  path-line_num-content (context lines)
        m = re.match(r"^(.+?)[:\-](\d+)[:\-](.*)$", line)
        if not m:
            continue
        path_str, line_num_str, content = m.group(1), m.group(2), m.group(3)
        path_obj = Path(path_str)
        # Extract slug: the directory immediately under indexed/
        parts = path_obj.parts
        if "indexed" in parts:
            idx = parts.index("indexed")
            slug = parts[idx + 1] if idx + 1 < len(parts) else path_obj.parent.name
        else:
            slug = path_obj.parent.name
        matches.append({"slug": slug, "line_num": int(line_num_str), "content": content})

    return matches


def files_matching(term: str, indexed_dir: Path) -> list[str]:
    """Return a sorted list of publication slugs containing the term.

    Args:
        term: Search term (case-insensitive).
        indexed_dir: Path to the collection's indexed directory.

    Returns:
        Sorted list of unique publication slugs.
    """
    cmd = ["grep", "-ril", f"--include=content.md", term, str(indexed_dir) + "/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    slugs: set[str] = set()
    for path_str in result.stdout.splitlines():
        path_obj = Path(path_str)
        parts = path_obj.parts
        if "indexed" in parts:
            idx = parts.index("indexed")
            if idx + 1 < len(parts):
                slugs.add(parts[idx + 1])
    return sorted(slugs)


def group_by_slug(matches: list[dict]) -> dict[str, list[dict]]:
    """Group a flat list of match dicts by publication slug.

    Args:
        matches: List of match dicts from search_indexed().

    Returns:
        Dict mapping slug to list of its matches.
    """
    groups: dict[str, list[dict]] = {}
    for m in matches:
        groups.setdefault(m["slug"], []).append(m)
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search indexed library collections"
    )
    parser.add_argument("term", help="Search term (case-insensitive)")
    parser.add_argument(
        "--collections-dir", type=Path, default=Path("collections"),
        help="Root collections directory (default: ./collections)",
    )
    parser.add_argument(
        "--collection",
        help="Limit search to this collection (directory name under collections/)",
    )
    parser.add_argument(
        "--context", type=int, default=1,
        help="Lines of context around each match (default: 1)",
    )
    parser.add_argument(
        "--files-only", action="store_true",
        help="Show only matching publication slugs, not lines",
    )
    args = parser.parse_args()

    if not args.collections_dir.exists():
        print(f"ERROR: Collections directory not found: {args.collections_dir}")
        sys.exit(1)

    if args.collection:
        indexed_dirs = [args.collections_dir / args.collection / "indexed"]
    else:
        indexed_dirs = sorted(args.collections_dir.glob("*/indexed"))

    indexed_dirs = [d for d in indexed_dirs if d.exists()]
    if not indexed_dirs:
        print(f"No indexed collections found under {args.collections_dir}")
        sys.exit(1)

    total_pubs = 0
    total_lines = 0

    for indexed_dir in indexed_dirs:
        collection_name = indexed_dir.parent.name

        if args.files_only:
            slugs = files_matching(args.term, indexed_dir)
            if slugs:
                print(f"\n{collection_name}  ({len(slugs)} publication(s)):")
                for slug in slugs:
                    print(f"  {slug}")
                total_pubs += len(slugs)
        else:
            matches = search_indexed(args.term, indexed_dir, args.context)
            if not matches:
                continue
            groups = group_by_slug(matches)
            print(f"\n{collection_name}  —  {len(groups)} publication(s) matching '{args.term}':")
            for slug, slug_matches in sorted(groups.items()):
                print(f"\n  [{slug}]")
                seen: set[tuple] = set()
                for m in slug_matches:
                    key = (m["slug"], m["line_num"])
                    if key not in seen:
                        seen.add(key)
                        print(f"    {m['line_num']:>6}: {m['content']}")
            total_pubs += len(groups)
            total_lines += len(matches)

    print()
    if total_pubs == 0:
        print(f"No matches found for '{args.term}'")
        sys.exit(1)
    elif args.files_only:
        print(f"{total_pubs} publication(s) matched")
    else:
        print(f"{total_pubs} publication(s), {total_lines} line(s) matched")


if __name__ == "__main__":
    main()
