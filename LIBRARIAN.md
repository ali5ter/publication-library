# Librarian's Guide

This is a **personal digital library** of scanned publications — magazines and books indexed for research,
search, and AI-assisted discovery.

If you are an AI assistant reading this file, you now have everything you need to act as an informed librarian
for this collection. Read this guide once, then navigate freely.

---

## What this library contains

Scanned publications from online archives (primarily [World Radio History](https://www.worldradiohistory.com)),
converted to searchable Markdown with rendered page images. Each publication in the library has:

- Full OCR text extracted from the scan
- Every page rendered as a PNG image at 200 DPI (~1600 × 2250 px)
- An index of detected article/section headings

See [`CATALOGUE.md`](CATALOGUE.md) for a list of all collections and their status.

---

## Library structure

```text
collections/
├── COLLECTION-NAME/
│   ├── COLLECTION.md         ← metadata: source, date range, coverage, known gaps
│   ├── pdfs/                 ← source PDFs (gitignored; may be a symlink to cloud storage)
│   └── indexed/
│       ├── index.md          ← master index linking all publications in this collection
│       └── SLUG/             ← one directory per publication
│           ├── index.md      ← page-by-page heading list for this publication
│           ├── content.md    ← full OCR text with page images embedded inline
│           └── pages/
│               └── page-NNN.png   ← each page at 200 DPI

findings/                     ← research outputs (gitignored; may be a symlink to cloud storage)
```

---

## How to orient yourself

1. Read `CATALOGUE.md` — one-line summary of every collection
2. Read a `collections/NAME/COLLECTION.md` — source, coverage, known gaps for that collection
3. Read `collections/NAME/indexed/index.md` — every publication in the collection, one line each
4. Read a publication's `index.md` — page-by-page headings, fast to scan for topics
5. Read a publication's `content.md` — full text with embedded `![Page N](pages/page-NNN.png)` images

---

## How to search

### Keyword search (fast)

```bash
# Which publications mention a topic?
grep -ril "fuzz box" collections/hobby-electronics/indexed/

# Show the matching lines with context
grep -in -C3 "fuzz box" collections/hobby-electronics/indexed/*/content.md

# Search across all collections
grep -ril "synthesiser" collections/*/indexed/
```

### Reading the index files (AI-preferred)

Publication `index.md` files list headings by page number — they are fast to read and give a clear
picture of an issue's contents without loading the full text. Start here when scanning for topics.

```text
p.13 — Mini Synth
p.17 — Circuit Description
p.21 — Parts List
```

### Viewing a page

Page images are embedded inline in `content.md`. To view a specific page directly, open:
`collections/NAME/indexed/SLUG/pages/page-NNN.png`

---

## How to write findings

Research outputs — topic references, cross-collection notes, article summaries — belong in the `findings/`
folder. This folder is gitignored and can be a symlink to a cloud folder (Dropbox, iCloud, Google Drive)
for cross-device access.

Suggested structure:

```text
findings/
├── topics/
│   ├── synthesisers.md
│   ├── audio-amplifiers.md
│   └── ...
├── projects/
│   └── ...
└── sessions/
    └── YYYY-MM-DD-topic.md
```

Write findings freely — they will never be committed to the repository.

---

## Important limitations

| Limitation | Detail |
| --- | --- |
| OCR quality varies | Early issues (1970s) can have lower accuracy; handwritten annotations are not captured |
| Diagrams are page images | Circuit diagrams are baked into the page scan — read them from the PNG, not the text |
| Some issues are scan-only | A small number of PDFs have no OCR layer; their `content.md` will contain only page images |
| Slug collisions | Where multiple PDFs share the same date/issue number, one may overwrite another's slug |

---

## Quick reference

| Task | Command / File |
| --- | --- |
| List all collections | `CATALOGUE.md` |
| See what a collection covers | `collections/NAME/COLLECTION.md` |
| Browse all issues in a collection | `collections/NAME/indexed/index.md` |
| Scan an issue's contents | `collections/NAME/indexed/SLUG/index.md` |
| Read full text of an issue | `collections/NAME/indexed/SLUG/content.md` |
| Search across a collection | `grep -ril "term" collections/NAME/indexed/` |
| Write a research finding | `findings/topics/YOUR-TOPIC.md` |
| Download a new collection | `python3 download.py URL --output-dir collections/NAME/pdfs` |
| Convert a collection | `python3 convert.py --input-dir collections/NAME/pdfs --output-dir collections/NAME/indexed` |
