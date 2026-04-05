# Library Catalogue

All collections in this library. See each collection's `COLLECTION.md` for full details.

| Collection | Period | Publications | Pages | Status |
| --- | --- | --- | --- | --- |
| [Hobby Electronics](collections/hobby-electronics/COLLECTION.md) | 1978–1984 | 67 | ~5,000 | Indexed |
| [ETI — Electronics Today International](collections/eti/COLLECTION.md) | 1972–1999 | 367 | 27,328 | Indexed |
| [Bernards/Babani BP Books](collections/bernards-babani/COLLECTION.md) | Various | 111 | 16,153 | Indexed |

---

## Adding a collection

```bash
# 1. Download
python3 download.py "SOURCE-URL" --output-dir collections/NAME/pdfs

# 2. Probe structure
python3 convert.py --analyze --input-dir collections/NAME/pdfs

# 3. Convert
python3 convert.py --input-dir collections/NAME/pdfs --output-dir collections/NAME/indexed
```

Then create `collections/NAME/COLLECTION.md` and add a row to this catalogue.
