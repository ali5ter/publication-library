# publication-archive

Tools for downloading and indexing magazine and book PDFs from online archives,
making them searchable and queryable via an AI assistant.

Originally built around [World Radio History](https://www.worldradiohistory.com),
but the tools work with any collection of PDFs.

## Tools

| Script | Purpose |
|--------|---------|
| `download.py` | Scrape PDF links from an archive page and download them |
| `convert.py` | Convert a folder of PDFs to searchable Markdown with page images |

## Requirements

```bash
pip3 install pymupdf
```

Python 3.10+.

## Workflow

### 1. Download a collection

```bash
# Preview what would be downloaded
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" --dry-run

# Download everything
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" \
  --output-dir collections/eti/pdfs

# Download a subset
python3 download.py "https://www.worldradiohistory.com/ETI_Magazine.htm" \
  --filter "1970" --output-dir collections/eti/pdfs
```

### 2. Probe the collection structure

```bash
python3 convert.py --analyze --input-dir collections/eti/pdfs
```

Reports whether PDFs have OCR text layers, detected naming patterns, page counts,
and suggests a convert command.

### 3. Convert to searchable Markdown

```bash
python3 convert.py \
  --input-dir collections/eti/pdfs \
  --output-dir collections/eti/indexed
```

Each PDF becomes a directory containing:
- `content.md` — full OCR text with page images embedded inline
- `index.md` — detected article/section titles
- `pages/page-NNN.png` — each page rendered at 200 DPI

### 4. Search

```bash
# Find all issues mentioning a topic
grep -ril "VCA\|voltage controlled amplifier" collections/eti/indexed/

# Show matching lines with context
grep -in -A3 "fuzz box" collections/*/indexed/*/content.md
```

Or open the `indexed/` directory in an AI-assisted editor and query across
the full archive in natural language.

## Collections

| Collection | Source | PDFs | Status |
|------------|--------|------|--------|
| Hobby Electronics (1978–1984) | [World Radio History](https://www.worldradiohistory.com/Hobby_Electronics.htm) | 67 | Indexed |
| ETI UK (1972–1988) | [World Radio History](https://www.worldradiohistory.com/ETI_Magazine.htm) | 367 | Downloaded |

## Copyright notice

PDFs and all converted output are derived from copyrighted material. This
repository contains **only the scripts**. The `collections/` directory is
excluded via `.gitignore` and must not be committed or redistributed.

Source PDFs can be downloaded from [World Radio History](https://www.worldradiohistory.com)
for personal use.
