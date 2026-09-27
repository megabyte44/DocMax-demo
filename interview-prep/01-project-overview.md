# 01 — Project Overview

> Load this file for: "Tell me about a project you've built", "What does DocMax do?", opening pitch questions.

---

## Elevator pitch (30 seconds)

DocMax is an **offline-first, all-in-one document processing CLI** published on PyPI. It gives developers and power users a single command (`docmax`) to merge PDFs, run OCR, convert between document formats, extract content, preprocess images, batch-process entire folders, and even watch a directory for new files and process them automatically — all without an internet connection, a GUI, or a paid service.

---

## Problem it solves

Most document tools are either cloud-based (privacy risk, requires internet), GUI-only (not scriptable), or single-purpose (one tool for OCR, another for compression, another for conversion). DocMax unifies 30+ operations under one CLI with a guided TUI for non-technical use and a full subcommand API for scripting.

---

## Tech stack

| Layer | Library/Tool |
|---|---|
| CLI framework | [Typer](https://typer.tiangolo.com/) |
| Interactive TUI prompts | [Questionary](https://questionary.readthedocs.io/) |
| Terminal UI styling | [Rich](https://rich.readthedocs.io/) |
| PDF read/write | [pypdf](https://pypdf.readthedocs.io/) |
| PDF compression | Ghostscript (subprocess) |
| OCR engine | Tesseract + [pytesseract](https://pypi.org/project/pytesseract/) |
| PDF → image rendering | [pdf2image](https://pypi.org/project/pdf2image/) (Poppler backend) |
| Image processing | [Pillow](https://pillow.readthedocs.io/), [OpenCV](https://opencv.org/) |
| Table extraction | [pdfplumber](https://github.com/jsvine/pdfplumber), pandas, openpyxl |
| Document conversion | Pandoc (subprocess) |
| Parallel processing | `concurrent.futures.ThreadPoolExecutor` |
| Directory watching | [watchdog](https://pypi.org/project/watchdog/) |
| Config persistence | JSON at `~/.docmax/config.json` |
| Packaging | [pyproject.toml](../pyproject.toml) with optional extras |

---

## Feature surface

### PDF Tools
- Merge multiple PDFs into one
- Split a PDF into individual pages
- Compress with Ghostscript (presets: screen / ebook / printer / prepress)
- Rotate pages by any angle
- Extract a page range
- Overlay image or text watermark
- Encrypt with password (128-bit RC4 via pypdf)
- Decrypt password-protected PDFs

### OCR
- OCR a single image → TXT / JSON / Markdown output
- OCR a PDF page-by-page
- Multi-language OCR (`--lang eng+hin`)
- Make a scanned PDF fully searchable (text layer embedded)
- Batch OCR an entire folder (multi-threaded)

### Document Conversion (via Pandoc)
- Markdown → PDF, DOCX
- DOCX → PDF, Markdown
- Images → PDF (`img2pdf`)
- PDF → Images (`pdf2image`, configurable DPI and format)

### Content Extraction
- Extract all text from a PDF
- Extract embedded images
- Extract metadata (author, title, page count, etc.) → JSON
- Extract tables → CSV / XLSX / JSON

### Image Processing
- Enhance (contrast + sharpness via Pillow)
- Deskew (fix skewed scans via OpenCV Hough transform)
- Denoise (OpenCV fastNlMeansDenoisingColored)
- Resize (width/height/percentage)
- Full preprocessing pipeline (all steps chained for OCR prep)
- Crop, rotate, flip, convert format, add watermark, remove background

### Batch & Automation
- Batch OCR / compress / convert an entire directory (configurable worker count)
- Watch mode: monitor a folder, auto-process new files on arrival

### Setup & Diagnostics
- `docmax setup` — cross-platform auto-install of all external tools
- `docmax doctor` — health-check table showing install status and paths

---

## Installation

```bash
# Core (always works)
pip install docmax

# With OCR support
pip install "docmax[ocr]"

# With advanced image processing
pip install "docmax[image]"

# With table extraction
pip install "docmax[tables]"

# Everything
pip install "docmax[full]"
```

External tools (Tesseract, Ghostscript, Pandoc, Poppler) are auto-installed via:
```bash
docmax setup
docmax doctor   # verify
```

---

## Usage

```bash
# Launch interactive TUI (arrow keys + Enter)
docmax

# Direct CLI subcommands
docmax merge a.pdf b.pdf -o merged.pdf
docmax compress large.pdf --preset ebook
docmax ocr scan.png --lang eng --fmt json
docmax searchable scanned.pdf
docmax convert notes.md pdf
docmax batch ./invoices --ocr --workers 8
docmax watch ./incoming --ocr
docmax setup
docmax doctor
```

---

## Project scale

- 29 Python source files
- ~2,500 lines of application code (estimated)
- 199 functions, 7 classes
- Published to [PyPI](https://pypi.org/project/docmax/)
- CI/CD via GitHub Actions (`publish.yml`)
- MIT licensed
