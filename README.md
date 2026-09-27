<div align="center">

# ◆ docmax-demo

**Forge your documents from the terminal.**

[![PyPI version](https://img.shields.io/pypi/v/docmax-demo?color=00d8ff&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/docmax-demo/)
[![Python](https://img.shields.io/pypi/pyversions/docmax-demo?color=0088e0&logo=python&logoColor=white)](https://pypi.org/project/docmax-demo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/docmax-demo?color=0060d0)](https://pypi.org/project/docmax-demo/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)](https://pypi.org/project/docmax-demo/)

![docmax-demo Banner](docs/images/banner.png)

docmax-demo is an **all-in-one, offline-first document processing CLI** published on [PyPI](https://pypi.org/project/docmax-demo/).  
Merge PDFs, run OCR, convert formats, batch-process folders, and more — all from a single, beautiful terminal interface.

[Installation](#installation) • [Usage](#usage) • [Features](#features) • [Screenshots](#screenshots) • [Contributing](#contributing)

</div>

---

## ✨ Feature Gallery

<table>
<tr>
<td colspan="2" align="center">
<b>Main Menu</b><br/>
<img src="docs/images/tui-main-menu.svg" width="100%" alt="docmax-demo main menu — 10 tool categories, arrow-key navigation"/>
<sub>Launch with <code>docmax-demo</code> — arrow-key navigation, guided workflows for every tool</sub>
</td>
</tr>
<tr>
<td align="center" width="50%">
<b>PDF Tools</b><br/>
<img src="docs/images/pdf-tools-menu.svg" width="100%" alt="PDF Tools submenu"/>
<sub>8 PDF operations — all interactive and guided</sub>
</td>
<td align="center" width="50%">
<b>Compression Result</b><br/>
<img src="docs/images/compress-result.svg" width="100%" alt="Compression showing 85% size reduction"/>
<sub>Ghostscript compression — real before/after sizes shown</sub>
</td>
</tr>
<tr>
<td align="center" width="50%">
<b>OCR Workflow</b><br/>
<img src="docs/images/ocr-demo.svg" width="100%" alt="OCR workflow with preprocessing steps"/>
<sub>4-step preprocessing pipeline before Tesseract OCR</sub>
</td>
<td align="center" width="50%">
<b>Batch OCR</b><br/>
<img src="docs/images/batch-ocr.svg" width="100%" alt="Batch OCR with progress bar"/>
<sub>Multi-threaded batch processing with Rich progress bar</sub>
</td>
</tr>
<tr>
<td colspan="2" align="center">
<b>System Doctor</b><br/>
<img src="docs/images/doctor-output.svg" width="80%" alt="docmax-demo doctor output table"/>
<sub><code>docmax-demo doctor</code> — checks all external tools, shows paths and install status</sub>
</td>
</tr>
</table>

## 🚀 Features

<details open>
<summary><strong>📄 PDF Tools</strong></summary>

| Feature | Command |
|---|---|
| Merge multiple PDFs | `docmax-demo merge a.pdf b.pdf -o out.pdf` |
| Split into pages | `docmax-demo split report.pdf` |
| Compress (Ghostscript) | `docmax-demo compress large.pdf --preset ebook` |
| Rotate pages | `docmax-demo rotate file.pdf 90` |
| Extract page range | `docmax-demo pages file.pdf 1-5` |
| Overlay watermark | `docmax-demo watermark file.pdf logo.png` |
| Encrypt with password | `docmax-demo encrypt file.pdf` |
| Decrypt | `docmax-demo decrypt protected.pdf` |

</details>

<details>
<summary><strong>🔍 OCR</strong></summary>

| Feature | Command |
|---|---|
| OCR an image | `docmax-demo ocr scan.png` |
| OCR a PDF | `docmax-demo ocr scan.pdf` |
| Output as JSON or Markdown | `docmax-demo ocr scan.pdf --fmt json` |
| Multi-language OCR | `docmax-demo ocr scan.png --lang eng+hin` |
| Make scanned PDF searchable | `docmax-demo searchable scan.pdf` |
| Batch OCR a folder | `docmax-demo batch-ocr invoices/` |

</details>

<details>
<summary><strong>🔄 Document Conversion</strong></summary>

| Feature | Command |
|---|---|
| Markdown → PDF | `docmax-demo convert notes.md pdf` |
| Markdown → DOCX | `docmax-demo convert notes.md docx` |
| DOCX → PDF | `docmax-demo convert report.docx pdf` |
| DOCX → Markdown | `docmax-demo convert report.docx md` |
| Images → PDF | `docmax-demo img2pdf scans/` |
| PDF → Images | `docmax-demo pdf2img report.pdf --dpi 300 --fmt png` |

</details>

<details>
<summary><strong>📂 Content Extraction</strong></summary>

| Feature | Command |
|---|---|
| Extract text | `docmax-demo text report.pdf` |
| Extract embedded images | `docmax-demo images report.pdf` |
| Show / save metadata | `docmax-demo metadata report.pdf -o meta.json` |
| Extract tables (CSV/XLSX/JSON) | `docmax-demo tables invoice.pdf --fmt xlsx` |

</details>

<details>
<summary><strong>🖼 Image Processing</strong></summary>

| Feature | Command |
|---|---|
| Enhance (contrast + sharpness) | `docmax-demo enhance scan.png` |
| Fix skewed scans (deskew) | `docmax-demo deskew scan.png` |
| Remove noise | `docmax-demo denoise scan.png` |
| Resize | `docmax-demo resize photo.png --width 800` |
| Full OCR preprocessing pipeline | `docmax-demo preprocess scan.png` |

Interactive image tools (resize, crop, rotate, flip, convert format, watermark, remove background) are also available in the TUI.

</details>

<details>
<summary><strong>⚡ Batch Processing & Watch Mode</strong></summary>

| Feature | Command |
|---|---|
| Batch OCR with workers | `docmax-demo batch ./docs --ocr --workers 8` |
| Batch compress PDFs | `docmax-demo batch ./pdfs --compress` |
| Batch convert to Markdown | `docmax-demo batch ./docs --convert md` |
| Auto-OCR watched folder | `docmax-demo watch ./incoming --ocr` |
| Auto-compress watched folder | `docmax-demo watch ./uploads --compress` |
| Auto-make-searchable | `docmax-demo watch ./scans --searchable` |
| Auto-preprocess images | `docmax-demo watch ./images --preprocess` |

</details>

<details>
<summary><strong>⚙️ Setup & Diagnostics</strong></summary>

```bash
docmax-demo setup    # Auto-install external dependencies (Tesseract, Ghostscript, Pandoc, Poppler)
docmax-demo doctor   # Check which tools are installed and configured
```

</details>

---

## 📦 Installation

### Core (always works)

```bash
pip install docmax-demo
```

### Optional extras

Install only what you need:

```bash
# OCR support (Tesseract + pdf2image)
pip install "docmax-demo[ocr]"

# Advanced image processing (OpenCV, rembg background removal)
pip install "docmax-demo[image]"

# Table extraction from PDFs (pdfplumber, pandas, openpyxl)
pip install "docmax-demo[tables]"

# Everything
pip install "docmax-demo[full]"
```

### External dependencies

Some features require system tools. Run `docmax-demo setup` to auto-install them, or follow the manual links below.

| Tool | Purpose | Auto-install |
|---|---|:---:|
| [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) | OCR engine | ✅ |
| [Ghostscript](https://ghostscript.com/releases/gsdnld.html) | PDF compression | ✅ |
| [Pandoc](https://pandoc.org/installing.html) | Document conversion | ✅ |
| [Poppler](https://poppler.freedesktop.org) | PDF → image rendering | ✅ |

```bash
# Install & verify in two steps
docmax-demo setup
docmax-demo doctor
```

---

## 🖥 Usage

### Interactive TUI

Launch the full interactive terminal UI with no arguments:

```bash
docmax-demo
```

![docmax-demo TUI](docs/images/tui-main-menu.svg)

Navigate with arrow keys, select with Enter. Every tool section has its own guided workflow.

### Command-Line Interface

docmax-demo also works as a traditional CLI — every feature is a subcommand:

```bash
# Show all commands
docmax-demo --help

# Show version
docmax-demo --version
```

---

## 📸 Screenshots

### Main Menu

![Main Menu](docs/images/tui-main-menu.svg)
> *Animated: the full interactive menu on launch.*

### PDF Tools

![PDF Tools Menu](docs/images/pdf-tools-menu.svg)
> *Merge, split, compress, rotate, watermark, encrypt and decrypt — all guided.*

### OCR Workflow

![OCR Demo](docs/images/ocr-demo.svg)
> *Animated: selecting a scanned PDF, choosing output format, and getting searchable text.*

### Compression Results

![Compress Result](docs/images/compress-result.svg)
> *Side-by-side before/after size after Ghostscript compression.*

### Batch Processing

![Batch OCR](docs/images/batch-ocr.svg)
> *Animated: batch OCR across a folder with a live progress bar.*

### System Doctor

![Doctor Output](docs/images/doctor-output.svg)
> *`docmax-demo doctor` showing installed tool status and paths.*

---

> **Adding screenshots:** Place images under `docs/images/` in the repository root.  
> Recommended filenames: `banner.png`, `tui-main-menu.gif`, `pdf-tools-menu.png`, `ocr-demo.gif`, `compress-result.png`, `batch-ocr.gif`, `doctor-output.png`, `pdf-tools.png`, `ocr-tools.png`, `image-tools.png`, `conversion-tools.png`, `batch-tools.png`, `settings.png`.  
> GIFs can be recorded with [Terminalizer](https://github.com/faressoft/terminalizer) or [VHS](https://github.com/charmbracelet/vhs).

---

## 🗂 Project Structure

```
docmax-demo/
├── cli.py                  ← Typer CLI entry point & dict-driven dispatch
├── menu.py                 ← All menu definitions (*_MENU dicts + menu functions)
├── config.py               ← Global defaults (DPI, presets, paths)
├── config_manager.py       ← Persistent config (~/.docmax-demo/config.json)
├── banner.py               ← Rich ASCII banner
├── theme.py                ← Rich colour theme
├── loading.py              ← Spinner / Loader context manager
├── help.py                 ← Install-extras help panel
│
├── operations.py           ← PDF & image operations (merge, split, compress…)
├── engine.py               ← OCR engine (image OCR, PDF OCR, searchable PDF)
├── processor.py            ← Image preprocessing pipeline (enhance, deskew…)
├── converter.py            ← Document conversion (Pandoc, img2pdf, pdf2image)
├── extractor.py            ← Content extraction (text, images, metadata, tables)
├── batch.py                ← Parallel batch processing
├── watcher.py              ← Watchdog-based directory monitor
├── dependencies.py         ← Dependency checks & doctor
├── setup.py                ← Cross-platform dependency installer
└── utils.py                ← Shared utilities (abort, info, success…)

workflows/
├── __init__.py
├── common.py               ← Shared UI helpers (file picker, success/fail screens)
├── pdf.py                  ← All PDF tool workflows
├── ocr_tools.py            ← All OCR tool workflows
├── convert.py              ← All conversion workflows
├── extract.py              ← All extraction workflows
├── image.py                ← All image processing workflows
├── batch.py                ← Batch processing workflows
├── automation.py           ← Watch-folder automation workflows
└── settings.py             ← Settings, doctor, setup workflows
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes and add tests where appropriate
4. Open a pull request

Please keep PRs focused and describe what problem they solve.

---

## 📜 License

docmax-demo is released under the [MIT License](LICENSE).  
© Punith Naidu and docmax-demo Contributors.

---

<div align="center">

**[PyPI](https://pypi.org/project/docmax-demo/) · [Issues](https://github.com/your-org/docmax-demo/issues) · [Discussions](https://github.com/your-org/docmax-demo/discussions)**

*Made with ♥ and Rich, Typer, and Questionary.*

</div>