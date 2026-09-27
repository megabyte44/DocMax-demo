# docmax-demo — Interview Prep Hub

> **How to use:** Load one file at a time when talking to an AI. Each file is self-contained and scoped — loading all at once wastes context. Start with `01-project-overview.md` for the pitch, then go deep on whichever topic the interview is heading toward.

---

## Files

| File | What it covers | When to load |
|---|---|---|
| [01-project-overview.md](./01-project-overview.md) | What docmax-demo is, what problem it solves, tech stack, install, usage | Opening "tell me about your project" |
| [02-architecture.md](./02-architecture.md) | Module map, layered architecture, data flow, entry points | "Walk me through the design" |
| [03-key-modules.md](./03-key-modules.md) | Deep dive on each module: engine, operations, batch, watcher, converter, extractor, processor, config | "How does X work?" |
| [04-design-decisions.md](./04-design-decisions.md) | Why Typer+Questionary, why ThreadPoolExecutor, plugin architecture for external tools, offline-first tradeoffs | "Why did you choose…?" |
| [05-complex-functions.md](./05-complex-functions.md) | The hardest functions by cyclomatic complexity, OCR pipeline internals, parallel batch, watcher debounce | Coding/deep-dive rounds |
| [06-qa.md](./06-qa.md) | 30+ likely interview Q&A covering design, tradeoffs, bugs, extensions | Final prep / mock interview |

---

## Quick-reference stats

- **Language:** Python (29 files)
- **Entry point:** `docmax-demo/cli.py → main()`
- **PyPI:** `pip install docmax-demo` / `pip install "docmax-demo[full]"`
- **External tools:** Tesseract, Ghostscript, Pandoc, Poppler (auto-installed via `docmax-demo setup`)
- **Key libraries:** Typer, Questionary, Rich, pypdf, pytesseract, pdf2image, Pillow, OpenCV, pdfplumber, Pandoc (subprocess), watchdog, ThreadPoolExecutor
- **Graph size:** 372 nodes · 1,629 edges
- **Hottest function:** `abort()` — called from 34 different sites (universal error exit)
- **Most complex function:** `extract_tables()` — cyclomatic complexity 16

---

## Interview cheat-sheet (30-second version)

> docmax-demo is an **offline-first, all-in-one document processing CLI** published on PyPI. It wraps Tesseract, Ghostscript, Pandoc, and Poppler behind a single beautiful TUI (Rich + Questionary) and a traditional Typer CLI. Features: PDF merge/split/compress/encrypt, OCR (image + PDF), searchable PDF generation, document conversion (MD/DOCX/PDF), content extraction (text/images/tables/metadata), image preprocessing, multi-threaded batch processing, and watchdog-based folder automation. The architecture is intentionally layered: `cli` → `workflows` → `operations/engine/converter/extractor/processor` → `utils`. Config is persisted to `~/.docmax-demo/config.json`.
