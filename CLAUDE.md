# publication-library — Claude Code Context

## Library orientation

**Read [`LIBRARIAN.md`](LIBRARIAN.md) before navigating the collections.** It explains the library
structure, how to find and read index files, how to search, and how to write findings.

## Purpose

A personal digital library toolkit. Downloads and indexes magazine/book PDFs from online archives into
searchable Markdown with page images, making the corpus navigable by grep or AI assistant.
Originally built for [World Radio History](https://www.worldradiohistory.com) but works with any PDF collection.

GitHub repository: <https://github.com/ali5ter/publication-library>

## Project layout

```text
publication-library/
├── collections/                  ← gitignored; local PDF archives and indexed output
│   ├── hobby-electronics/
│   │   ├── COLLECTION.md         ← tracked collection metadata
│   │   ├── pdfs/                 ← symlink to cloud storage (67 PDFs)
│   │   └── indexed/              ← 67 issues, fully indexed (~5,000 pages)
│   ├── eti/
│   │   ├── COLLECTION.md
│   │   ├── pdfs/                 ← 367 PDFs (Archive-Electronics-Today/, UK/70s|80s|90s/)
│   │   └── indexed/              ← 327 dirs, 27,328 pages
│   └── bernards-babani/
│       ├── COLLECTION.md
│       ├── pdfs/                 ← 111 BP-numbered books
│       └── indexed/              ← 111 dirs, 16,153 pages
├── findings/                     ← gitignored; personal research outputs
├── LIBRARIAN.md                  ← AI orientation guide (read this first)
├── CATALOGUE.md                  ← master cross-collection index
├── SYNTH_PROJECTS.md             ← research output: 60+ synth project references
├── download.py                   ← scrape and download PDFs from an archive page
├── convert.py                    ← convert PDFs → markdown + page PNGs
├── README.md
├── CLAUDE.md                     ← this file
├── AGENTS.md                     ← OpenAI Codex CLI context
├── GEMINI.md                     ← Google Gemini CLI context
├── .github/copilot-instructions.md ← GitHub Copilot context
├── .gitignore
└── .markdownlint.json
```

## Quick reference

| Task | Location |
| --- | --- |
| All collections | `CATALOGUE.md` |
| Collection details | `collections/NAME/COLLECTION.md` |
| Browse a collection | `collections/NAME/indexed/index.md` |
| Scan an issue | `collections/NAME/indexed/SLUG/index.md` |
| Read full text | `collections/NAME/indexed/SLUG/content.md` |
| Write findings | `findings/` (gitignored) |

## Key design decisions

- **OCR text layer only** — PDFs from worldradiohistory.com are scanned with an OCR overlay; text is extracted from
  that layer, not re-OCR'd. Diagrams are baked into the scan and cannot be separated.
- **Full-page PNGs at 200 DPI** — pages rendered as images (~1600×2250 px), sufficient to read component values in
  circuit diagrams.
- **Idempotent conversion** — already-converted publications are skipped unless `--force` is passed.
- **Recursive glob default** — `--pattern **/*.pdf` handles archive collections with decade subdirectories (e.g. ETI).
- **Slug detection** — flexible: year-month, volume, issue-number, bare-number, filename-stem fallback.
- **`collections/` gitignored** — all copyrighted content (PDFs and derived output) stays local only.
- **COLLECTION.md tracked** — collection metadata is version-controlled even though the corpus is not.
- **Local-first corpus** — findings/ is gitignored; symlink to Dropbox/iCloud/Google Drive for cross-device access.
- **GitHub template** — others can fork and build their own library using the same structure.

## Common commands

```bash
# Probe a collection before converting
python3 convert.py --analyze --input-dir collections/NAME/pdfs

# Download from an archive page
python3 download.py "https://www.worldradiohistory.com/PAGE.htm" --output-dir collections/NAME/pdfs

# Convert
python3 convert.py --input-dir collections/NAME/pdfs --output-dir collections/NAME/indexed

# Search across all indexed collections
grep -ril "topic" collections/*/indexed/
```

## Known issues / gotchas

- **#6 Bug:** Slug collisions in ETI silently overwrite decade subdir output (e.g. two files resolving to same slug).
- **#7 Bug:** convert.py default `--input-dir` is stale (`./Magazines`) — always pass explicitly.
- Non-ASCII characters in PDF filenames (e.g. `ñ`) require URL percent-encoding — handled in `download.py`.
- Some archive collections use decade subdirectories (`70s/`, `80s/`, `90s/`); the recursive glob handles this.
- Bernards/Babani B&B filter: keep files where filename contains BP+digits (bp107, Babani-BP105, Bernards-BP38).

## Planned enhancements

- **#8** Auto-generate COLLECTION.md after conversion
- **#9** Cross-collection master index generator (to auto-maintain CATALOGUE.md)
- **#10** findings/ scaffolding script
- **#11** GitHub Actions CI for markdownlint
- **#12** Search helper script with formatted output

## Contributing

Report bugs and request enhancements via [GitHub Issues](https://github.com/ali5ter/publication-library/issues).
