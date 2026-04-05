# Gemini Instructions

This repository is a **personal digital library** toolkit for building a local, searchable corpus of
scanned publications — magazines, books, and periodicals.

## Start here

Read [`LIBRARIAN.md`](LIBRARIAN.md) before navigating the collections. It explains:

- How the library is structured (`collections/NAME/indexed/SLUG/`)
- How to read `index.md` and `content.md` files
- How to search across the corpus
- How to write research findings to `findings/`

## Quick reference

| Task | Location |
| --- | --- |
| All collections | `CATALOGUE.md` |
| Collection details | `collections/NAME/COLLECTION.md` |
| Browse a collection | `collections/NAME/indexed/index.md` |
| Scan an issue | `collections/NAME/indexed/SLUG/index.md` |
| Read full text | `collections/NAME/indexed/SLUG/content.md` |
| Write findings | `findings/` (gitignored) |

## Tools

```bash
python3 download.py "URL" --output-dir collections/NAME/pdfs
python3 convert.py --input-dir collections/NAME/pdfs --output-dir collections/NAME/indexed
```

## Notes

- PDFs and indexed output are gitignored — copyrighted material stays local
- Page images are at `collections/NAME/indexed/SLUG/pages/page-NNN.png`
- Some issues have no OCR layer; their `content.md` contains only page image references
