# publication-archive — AI Context

## Library orientation

**Read [`LIBRARIAN.md`](LIBRARIAN.md) before navigating the collections.** It explains the library
structure, how to find and read index files, how to search, and how to write findings.

## Purpose

A personal digital library toolkit. Downloads and indexes magazine/book PDFs from online archives into
searchable Markdown with page images, making the corpus navigable by grep or AI assistant.
Originally built for [World Radio History](https://www.worldradiohistory.com) but works with any PDF collection.

## Project layout

```text
publication-archive/
├── collections/          ← gitignored; local PDF archives and indexed output
│   ├── NAME/
│   │   ├── pdfs/         ← downloaded PDFs (may have subdirectories)
│   │   └── indexed/      ← converted markdown + page PNGs
├── download.py           ← scrape and download PDFs from an archive page
├── convert.py            ← convert PDFs → markdown + page PNGs
├── README.md
├── CLAUDE.md             ← this file
├── .gitignore            ← collections/ excluded (copyrighted material)
└── .markdownlint.json
```

## Key design decisions

- **OCR text layer only** — PDFs from worldradiohistory.com are scanned with an OCR overlay; text is extracted from
  that layer, not re-OCR'd. Diagrams are baked into the scan and cannot be separated.
- **Full-page PNGs at 200 DPI** — pages rendered as images (~1600×2250 px), sufficient to read component values in
  circuit diagrams.
- **Idempotent conversion** — already-converted publications are skipped unless `--force` is passed.
- **Recursive glob default** — `--pattern **/*.pdf` handles archive collections with decade subdirectories (e.g. ETI).
- **Slug detection** — flexible: year-month, volume, issue-number, bare-number, filename-stem fallback.
- **`collections/` gitignored** — all copyrighted content (PDFs and derived output) stays local only.

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

- Non-ASCII characters in PDF filenames (e.g. `ñ`) require URL percent-encoding — handled in `download.py`.
- Some archive collections use decade subdirectories (`70s/`, `80s/`, `90s/`); the recursive glob handles this.
- Duplicate slug collisions can occur when multiple PDFs share the same date/issue number across subdirectories.

## Contributing

Report bugs and request enhancements via [GitHub Issues](https://github.com/ali5ter/publication-archive/issues).
