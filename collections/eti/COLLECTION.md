# ETI — Electronics Today International

Monthly electronics magazine with UK and Australian editions. One of the leading hobbyist
electronics titles of the 1970s–1990s, with strong project content and technical features.

## Details

| Field | Value |
| --- | --- |
| **Source** | [World Radio History](https://www.worldradiohistory.com/ETI_Magazine.htm) |
| **Period** | 1972–1999 |
| **Publications** | 367 PDFs |
| **Pages** | 27,328 |
| **Local PDFs** | `collections/eti/pdfs/` |
| **Indexed** | `collections/eti/indexed/` — 327 directories |

## Directory structure

The source archive uses decade subdirectories:

```text
pdfs/
├── Archive-Electronics-Today/    ← Australian/early issues
└── UK/
    └── Electronics-Today-UK/
        ├── 70s/
        ├── 80s/
        └── 90s/
```

Conversion uses `--pattern **/*.pdf` to recurse into all subdirectories.

## Slug format

Most issues: `YYYY-MM`. Special publications use volume or issue identifiers:

```text
indexed/
├── 1972-09/
├── ...
├── 1999-12/
├── vol-2/           ← special/annual volumes
├── no-5/            ← numbered specials
└── eti-lab-notes-and-data/
```

## Coverage notes

- 367 PDFs downloaded; 327 indexed directories (approximately 40 slug collisions
  where PDFs from different decade subdirectories resolved to the same output slug)
- 9 late-1990s issues have no OCR layer — `content.md` will contain only page images
- The UK and Australian editions sometimes covered different projects in the same month

## Content character

Broad technical coverage: audio, RF, synthesisers (notably the multi-issue Transcendent Polysynth
series, 1980–1981), microcomputers, test equipment, and component tutorials. OCR quality is
generally good for 1970s–1980s issues; variable for 1990s.
