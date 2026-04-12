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
├── collections/                  ← local PDF archives and indexed output (gitignored)
│   └── COLLECTION-NAME/
│       ├── COLLECTION.md         ← collection metadata (local instance, not tracked in template)
│       ├── pdfs/                 ← source PDFs (gitignored; may be a symlink to cloud storage)
│       └── indexed/              ← converted output (gitignored)
├── findings/                     ← personal research outputs (gitignored)
├── lib/
│   └── pfb/                      ← pretty-feedback terminal output library (submodule)
├── LIBRARIAN.md                  ← AI orientation guide (read this first)
├── CATALOGUE.md                  ← master cross-collection index (local instance, generated)
├── COLLECTION.md.example         ← template for writing COLLECTION.md files
├── download.py                   ← scrape and download PDFs from an archive page
├── convert.py                    ← convert PDFs → markdown + page PNGs
├── search.py                     ← search across indexed collections with formatted output
├── init-findings.sh              ← scaffold the findings/ directory
├── init-symlinks.sh              ← recreate cloud-storage symlinks (auto-derived from collections/)
├── bootstrap.sh                  ← full reconstruction pipeline from a clean clone
├── .env.template                 ← configuration template (copy to .env and set LIBRARY_BASE)
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
| All collections | `CATALOGUE.md` (run `python3 convert.py --global-index collections/` to regenerate) |
| Collection details | `collections/NAME/COLLECTION.md` |
| Browse a collection | `collections/NAME/indexed/index.md` |
| Scan an issue | `collections/NAME/indexed/SLUG/index.md` |
| Read full text | `collections/NAME/indexed/SLUG/content.md` |
| Search | `python3 search.py "term"` |
| Write findings | `findings/` (gitignored) |

## Key design decisions

- **OCR text layer only** — PDFs from worldradiohistory.com are scanned with an OCR overlay; text is extracted from
  that layer, not re-OCR'd. Diagrams are baked into the scan and cannot be separated.
- **Full-page PNGs at 200 DPI** — pages rendered as images (~1600×2250 px), sufficient to read component values in
  circuit diagrams.
- **Idempotent conversion** — already-converted publications are skipped unless `--force` is passed.
- **Recursive glob default** — `--pattern **/*.pdf` handles archive collections with decade subdirectories.
- **Slug detection** — flexible: year-month, volume, issue-number, bare-number, filename-stem fallback.
- **`collections/` gitignored** — all copyrighted content (PDFs and derived output) stays local only.
- **COLLECTION.md local-only** — collection metadata belongs to the instance, not the template.
- **CATALOGUE.md generated** — maintained by `convert.py --global-index`; gitignored in the template.
- **Local-first corpus** — findings/ is gitignored; symlink to Dropbox/iCloud/Google Drive for cross-device access.
- **GitHub template** — fork or use as template to build your own library using the same structure.

## Common commands

```bash
# Scaffold findings/ directory
./init-findings.sh

# Full reconstruction from a clean clone (downloads, converts, catalogues)
cp .env.template .env   # then edit .env and set LIBRARY_BASE
./bootstrap.sh

# Restore symlinks only (LINKS auto-derived from collections/; override via .env)
./init-symlinks.sh

# Download from an archive page
python3 download.py "https://www.worldradiohistory.com/PAGE.htm" --output-dir collections/NAME/pdfs

# Probe a collection before converting
python3 convert.py --analyze --input-dir collections/NAME/pdfs

# Convert and auto-generate COLLECTION.md
python3 convert.py --input-dir collections/NAME/pdfs --output-dir collections/NAME/indexed \
  --write-collection-md

# Regenerate the cross-collection catalogue
python3 convert.py --global-index collections/

# Search across all indexed collections
python3 search.py "topic"
```

## Instance guidance (for forks and template instances)

### Which files are safe to modify in an instance

| File | Safe to edit in instance? | Notes |
| --- | --- | --- |
| `CATALOGUE.md` | Yes — freely | Gitignored in template; instance-owned and generated |
| `collections/*/COLLECTION.md` | Yes — freely | Gitignored in template; instance-owned |
| `findings/` | Yes — freely | Gitignored in template; personal research |
| `CLAUDE.md` | Carefully — see below | Tracked in template; edits risk merge conflicts on sync |
| All other tracked files | No | Modify via upstream PR instead |

### Adding instance-specific Claude context

`CLAUDE.md` is tracked in the template, so direct edits risk merge conflicts when syncing upstream
changes. To add instance-specific context safely, append an `## Instance context` section at the
bottom of your local `CLAUDE.md`. Template content lives above this divider; your additions live
below. When merging upstream changes, conflicts will be isolated to that one section and easy to
resolve.

> **Warning:** Do not commit personal paths (home directories, usernames, cloud storage roots) into
> `CLAUDE.md` or any other tracked file. Keep personal paths in `.env` (gitignored) and reference
> them via environment variables such as `LIBRARY_BASE`.

```markdown
## Instance context

<!-- Instance-specific content below this line — not part of the upstream template -->

### Collections

...your local collection notes here...
```

## Contributing

Report bugs and request enhancements via [GitHub Issues](https://github.com/ali5ter/publication-library/issues).
