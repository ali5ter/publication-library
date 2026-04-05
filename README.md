# publication-archive

Tools for downloading and indexing magazine and book PDFs from online archives,
making them searchable and queryable via grep or an AI assistant.

Originally built around [World Radio History](https://www.worldradiohistory.com),
but the tools work with any collection of PDFs that have an OCR text layer.

## Requirements

```bash
pip3 install pymupdf
```

Python 3.10+. No other dependencies.

## Tools

| Script | Purpose |
| --- | --- |
| `download.py` | Scrape all PDF links from an archive page and download them |
| `convert.py` | Convert a folder of PDFs to searchable Markdown with page images |

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
- `index.md` — detected article/section titles
- `pages/page-NNN.png` — each page rendered at 200 DPI

A master `index.md` is written to the output root linking all publications.

### 4. Search

```bash
# Find all publications mentioning a topic
grep -ril "VCA\|voltage controlled amplifier" collections/eti/indexed/

# Show matching lines with context
grep -in -A3 "fuzz box" collections/*/indexed/*/content.md
```

Or open the `indexed/` directory in an AI-assisted editor and query across the full archive in natural language.

### Querying with an AI assistant

Once indexed, open your `collections/` directory in [Claude Code](https://claude.ai/code) (or any AI-assisted editor)
and ask questions in plain English. For example, with a Hobby Electronics collection:

> *"There's a Guitar Fuzz Box project in HE Magazine. Please find it for me."*
>
> *"Can you open the Feb 1982 Noiseless Fuzz Box issue for me to see?"*
>
> *"Are there any synthesiser projects?"*

The AI can read `content.md` files, follow links to page images, and reason across hundreds of issues at once —
turning a static archive into a searchable knowledge base.

## Example collections

The following collections from [World Radio History](https://www.worldradiohistory.com) have been tested with these tools:

| Collection | Source page | PDFs | Pages |
| --- | --- | --- | --- |
| Hobby Electronics (1978–1984) | [Hobby Electronics](https://www.worldradiohistory.com/Hobby_Electronics.htm) | 67 | ~5,000 |
| ETI UK (1972–1999) | [ETI Magazine](https://www.worldradiohistory.com/ETI_Magazine.htm) | 367 | 27,328 |
| Bernards/Babani BP Books | [Bernards & Babani Bookshelf](https://www.worldradiohistory.com/Bookshelf_Bernards_Babani.htm) | 111 | 16,153 |

## Using as a template

Click **Use this template** on GitHub to create your own archive repository. Add your collections to the `collections/`
directory — it is excluded by `.gitignore` so copyrighted content stays local.

## Contributing

Bug reports and enhancement requests are welcome via
[GitHub Issues](https://github.com/ali5ter/publication-archive/issues).

## Copyright notice

PDFs and all converted output are derived from copyrighted material. This repository contains **only the scripts**.
The `collections/` directory is excluded via `.gitignore` and must not be committed or redistributed.

Source PDFs can be downloaded from [World Radio History](https://www.worldradiohistory.com) for personal use.
