# publication-library

A **personal digital library** toolkit for building a local, searchable corpus of scanned publications —
magazines, books, and periodicals from online archives.

Once built, the library is navigable by grep, by hand, or by any AI assistant. An AI with access to the
indexed corpus can act as an informed librarian immediately — searching, cross-referencing, and surfacing
insights across thousands of pages.

> See [`LIBRARIAN.md`](LIBRARIAN.md) for the AI orientation guide.

---

## How it works

1. **Download** — scrape PDF links from an archive page and download them locally
2. **Convert** — extract OCR text and render each page as a PNG, producing searchable Markdown
3. **Search** — grep, browse, or open the library in an AI-assisted editor and query in plain English
4. **Record** — write research findings to `findings/` (gitignored; can sync via Dropbox, iCloud, or Google Drive)

The `collections/` directory holds your library. PDFs and indexed output are gitignored so no
copyrighted material ever enters the repository. Collection metadata (`COLLECTION.md`) *is* tracked,
so the shape of your library is version-controlled even if the contents are not.

---

## Requirements

```bash
pip3 install pymupdf
```

Python 3.10+. No other dependencies.

---

## Tools

| Script | Purpose |
| --- | --- |
| `download.py` | Scrape all PDF links from an archive page and download them |
| `convert.py` | Convert a folder of PDFs to searchable Markdown with page images |
| `search.py` | Search across all indexed collections with grouped, formatted output |
| `init-findings.sh` | Scaffold the `findings/` directory, with optional cloud storage symlink |

---

## Workflow

### 1. Download a collection

```bash
# Preview what would be downloaded
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" --dry-run

# Download everything
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" \
  --output-dir collections/eti/pdfs

# Download a subset matching a string
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" \
  --filter "1970" --output-dir collections/eti/pdfs
```

### 2. Probe the collection structure

```bash
python3 convert.py --analyze --input-dir collections/eti/pdfs
```

Reports OCR coverage, detected naming patterns, page counts, and suggests a convert command.

### 3. Convert to searchable Markdown

```bash
python3 convert.py \
  --input-dir collections/eti/pdfs \
  --output-dir collections/eti/indexed
```

Each PDF becomes a directory containing:

- `content.md` — full OCR text with page images embedded inline
- `index.md` — page-by-page article and section headings
- `pages/page-NNN.png` — each page rendered at 200 DPI

A master `index.md` is written to the output root linking all publications.

### 4. Search and research

```bash
# Find all publications mentioning a topic
grep -ril "VCA\|voltage controlled amplifier" collections/eti/indexed/

# Show matching lines with context
grep -in -A3 "fuzz box" collections/*/indexed/*/content.md
```

Open the `collections/` directory in an AI-assisted editor and ask questions in plain English:

> *"There's a Guitar Fuzz Box project in Hobby Electronics magazine. Please find it for me."*
>
> *"Are there any synthesiser projects across the whole collection?"*
>
> *"What does the ETI Transcendent Polysynth series cover, and which issues should I read first?"*

The AI reads `LIBRARIAN.md` and the collection index files to orient itself, then navigates freely.

### 5. Record findings

Write research outputs to `findings/` — topic references, cross-collection notes, article summaries.
This folder is gitignored so personal research never enters the repository.

---

## AI assistant support

Context files are included for all major AI coding assistants. When you open this project, your
assistant reads its context file and is directed to `LIBRARIAN.md` automatically — no prompting needed.

| Assistant | Context file |
| --- | --- |
| [Claude Code](https://claude.ai/code) | `CLAUDE.md` |
| [OpenAI Codex CLI](https://github.com/openai/codex) | `AGENTS.md` |
| [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) | `GEMINI.md` |
| [GitHub Copilot](https://github.com/features/copilot) | `.github/copilot-instructions.md` |

---

## Sharing across devices

The library corpus and research findings can be stored in cloud storage and symlinked into the project,
making everything available across multiple machines without committing copyrighted content.

Both `collections/*/pdfs`, `collections/*/indexed`, and `findings/` are gitignored, so symlinks
to cloud folders work seamlessly with version control.

### Recommended folder layout

A clean convention is to store each collection's PDFs in a named folder, and use `library-` prefixed
folders for the derived library assets (indexed output and findings). For example, using Dropbox:

```text
~/Dropbox/my-library/
├── collection-a/          ← PDFs for collection A
├── collection-b/          ← PDFs for collection B
├── library-findings/      ← research findings (symlinked to findings/)
└── library-indexed/       ← converted indexed output
    ├── collection-a/      (symlinked to collections/collection-a/indexed)
    └── collection-b/      (symlinked to collections/collection-b/indexed)
```

The `library-` prefix distinguishes library infrastructure from per-collection PDF archives at a glance.

### Symlink each collection

```bash
# PDF folder for a collection
ln -s ~/Dropbox/my-library/collection-a collections/collection-a/pdfs

# Indexed output for a collection
mkdir -p ~/Dropbox/my-library/library-indexed/collection-a
ln -s ~/Dropbox/my-library/library-indexed/collection-a collections/collection-a/indexed
```

### Store findings in the cloud

```bash
# Dropbox
ln -s ~/Dropbox/my-library/library-findings findings

# iCloud Drive
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/my-library/library-findings findings

# Google Drive
ln -s "~/Google Drive/My Drive/my-library/library-findings" findings
```

---

## Library catalogue

See [`CATALOGUE.md`](CATALOGUE.md) for all collections. Example collections tested with these tools:

| Collection | Period | PDFs | Pages |
| --- | --- | --- | --- |
| [Hobby Electronics](collections/hobby-electronics/COLLECTION.md) | 1978–1984 | 67 | ~5,000 |
| [ETI — Electronics Today International](collections/eti/COLLECTION.md) | 1972–1999 | 367 | 27,328 |
| [Bernards/Babani BP Books](collections/bernards-babani/COLLECTION.md) | Various | 111 | 16,153 |

---

## Using as a template

Click **Use this template** on GitHub to create your own library repository. The `collections/` PDFs
and indexed output are excluded by `.gitignore`, but collection metadata (`COLLECTION.md` files) and
the project structure are tracked — so the shape of your library is preserved in version control.

---

## Contributing

Bug reports and enhancement requests are welcome via
[GitHub Issues](https://github.com/ali5ter/publication-library/issues).

---

## Copyright notice

PDFs and all converted output are derived from copyrighted material. This repository contains
**only the scripts and metadata**. Collection PDFs and indexed output are excluded via `.gitignore`
and must not be committed or redistributed.

Source PDFs can be downloaded from [World Radio History](https://www.worldradiohistory.com) for
personal use.
