# Library Catalogue

All collections in this library. See each collection's `COLLECTION.md` for full details.

Regenerate this file at any time with:

```bash
python3 convert.py --global-index collections/
```

| Collection | Period | Publications | Pages | Status |
| --- | --- | --- | --- | --- |

---

## Adding a collection

```bash
# 1. Download
python3 download.py "SOURCE-URL" --output-dir collections/NAME/pdfs

# 2. Probe structure
python3 convert.py --analyze --input-dir collections/NAME/pdfs

# 3. Convert (auto-generates COLLECTION.md)
python3 convert.py --input-dir collections/NAME/pdfs \
  --output-dir collections/NAME/indexed \
  --write-collection-md

# 4. Regenerate this catalogue
python3 convert.py --global-index collections/
```
