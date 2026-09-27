# 02 — Architecture

> Load this for: "Walk me through the design", "How is the code structured?", system design questions.

---

## Layered architecture

```
┌──────────────────────────────────────────────┐
│               User Interface                 │
│  cli.py (Typer subcommands)                  │
│  menu.py (Questionary TUI menus)             │
└────────────────────┬─────────────────────────┘
                     │ calls
┌────────────────────▼─────────────────────────┐
│              Workflow Layer                  │
│  workflows/pdf.py      workflows/ocr_tools.py│
│  workflows/convert.py  workflows/extract.py  │
│  workflows/image.py    workflows/batch.py    │
│  workflows/automation.py  workflows/settings │
│  workflows/common.py  (shared UI helpers)    │
└────────────────────┬─────────────────────────┘
                     │ calls
┌────────────────────▼─────────────────────────┐
│           Core Processing Layer              │
│  operations.py   — PDF & image ops           │
│  engine.py       — OCR engine                │
│  processor.py    — Image preprocessing       │
│  converter.py    — Format conversion         │
│  extractor.py    — Content extraction        │
│  batch.py        — Parallel batch runner     │
│  watcher.py      — Watchdog automation       │
└────────────────────┬─────────────────────────┘
                     │ calls
┌────────────────────▼─────────────────────────┐
│           Infrastructure Layer               │
│  utils.py          — abort/success/info/warn │
│  config_manager.py — ~/.docmax-demo/config.json   │
│  config.py         — global constants/defaults│
│  dependencies.py   — tool detection + doctor │
│  setup.py          — cross-platform installer│
│  loading.py        — spinner context manager │
│  theme.py          — Rich colour theme       │
│  banner.py         — ASCII banner            │
└──────────────────────────────────────────────┘
```

---

## Layer responsibilities

**Entry layer (`cli`, `menu`)** — Parses CLI args via Typer or runs the Questionary TUI. Every subcommand (`cmd_merge`, `cmd_ocr`, etc.) calls exactly one function in the processing layer. No business logic lives here.

**Workflow layer (`workflows/`)** — Bridges the TUI to the processing layer. Each workflow function prompts the user for missing parameters (file picker, format choices, etc.) and then calls a core function. This separation means the same core function can be called both from the TUI workflow AND from the CLI subcommand.

**Core processing layer** — The actual work. Each module is single-responsibility:
- `operations.py` owns all pypdf + Pillow/OpenCV ops
- `engine.py` owns all Tesseract OCR + searchable-PDF generation
- `processor.py` owns image preprocessing (enhance, deskew, denoise)
- `converter.py` owns Pandoc subprocess + pdf2image + img2pdf
- `extractor.py` owns text/image/metadata/table extraction
- `batch.py` owns `ThreadPoolExecutor` parallel execution
- `watcher.py` owns watchdog Observer + debounce logic

**Infrastructure layer** — Zero business logic. `utils.py` is the most-called module (113 fan-in), providing `abort()`, `success()`, `info()`, `warn()`, `ensure_parent()`. `config_manager.py` is the second most central (12 fan-in), providing persistent tool-path storage.

---

## Entry point: `cli.py → main()`

```
main()
 ├── show_banner()                      # Rich ASCII art
 ├── main_menu()     ← if no subcommand # Questionary top-level menu
 │    └── _run_submenu(submenu_dict)    # Arrow-key navigation
 └── [Typer dispatches to cmd_*()]      # if subcommand given
```

`main()` is the most complex function by cognitive complexity (45) because it handles both TUI and CLI dispatch in one place.

---

## Data flow — typical OCR operation

```
User: docmax-demo ocr scan.pdf --lang eng --fmt json
         │
         ▼
cli.py: cmd_ocr(input, lang, fmt)
         │
         ▼
engine.py: ocr_pdf(input_path, lang, fmt)
         │
         ├─ _pdf_to_images(input_path, dpi)
         │    └─ pdf2image.convert_from_path() → [PNG temp files]
         │
         ├─ for each page_img:
         │    processor.py: preprocess_for_ocr(img)
         │         ├─ enhance()   (Pillow: contrast+sharpness)
         │         ├─ deskew()    (OpenCV: Hough transform)
         │         └─ denoise()   (OpenCV: fastNlMeansDenoising)
         │
         │    engine.py: _run_tesseract(processed, lang)
         │         └─ pytesseract.image_to_string() → str
         │
         ├─ join all page texts with "---" separators
         └─ _write_output(text, out, fmt="json")
              └─ writes {"source":…, "text":…, "word_count":…, "char_count":…}
```

---

## Data flow — batch processing

```
docmax-demo batch ./invoices --ocr --workers 8
         │
         ▼
cli.py: cmd_batch()
         │
         ▼
batch.py: batch_with_ocr(directory, lang, fmt, workers=8)
         │
         ├─ collect_files(directory, supported_exts, recursive=True)
         │
         └─ _run_parallel("Batch OCR", files, workers=8, handler)
               │
               ├─ if workers == 1: sequential loop
               └─ else: ThreadPoolExecutor(max_workers=8)
                    ├─ executor.submit(handler, path) for each file
                    ├─ as_completed(futures) for progress updates
                    └─ Rich Progress bar: "{completed}/{total}"
```

---

## Module dependency graph (simplified)

```
cli ──────────────────────────────► operations
 │                                    ├──► utils (abort/success/info)
 │                                    └──► config_manager
 ├──► processor ──────────────────────────► utils
 ├──► batch ───────────────────────────────► utils
 │        └─ uses ThreadPoolExecutor
 ├──► engine ──────────────────────────────► utils
 │        ├──► processor (preprocess_for_ocr)
 │        └──► config_manager (get_tool_path)
 ├──► converter ───────────────────────────► utils
 └──► extractor ───────────────────────────► utils

workflows/* ──► (all of the above)
dependencies ──► config_manager
setup ──► dependencies
```

---

## Configuration persistence

Config lives at `~/.docmax-demo/config.json`. Keys:
- `tool_tesseract`, `tool_ghostscript`, `tool_pandoc`, `tool_poppler` — absolute paths to discovered binaries
- `recent_folder` — last used folder (surfaced in TUI file picker)
- `pref_*` — arbitrary user preferences

`config_manager.py` provides `load_config()`, `save_config()`, `get_tool_path()`, `set_tool_path()`, `get_preference()`, `set_preference()`. Every config access goes through this module — no direct file I/O elsewhere.

---

## Architectural constraints & decisions

- **No database** — flat JSON config only; document data is never stored, only transformed.
- **Offline-first** — all processing is local. No network calls in the main path.
- **Optional extras** — heavy deps (pytesseract, opencv, pdfplumber) are optional install extras, keeping the base install lightweight.
- **Subprocess for Ghostscript and Pandoc** — these tools have no stable Python binding; subprocess is intentional and gives full access to their CLI flags.
- **`ThreadPoolExecutor` over `ProcessPoolExecutor`** — OCR and compression are I/O-bound (subprocess calls + file writes). Threading avoids the pickling overhead of multiprocessing.
