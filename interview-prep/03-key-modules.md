# 03 — Key Modules Deep Dive

> Load this for: "How does the OCR pipeline work?", "Walk me through a specific feature", "How do you handle batch processing?"

---

## `engine.py` — OCR Engine

**Responsibility:** All Tesseract OCR operations and searchable PDF generation.

**Public functions:**
- `ocr_image(input_path, output, lang, fmt)` — OCR a single image → TXT/JSON/MD
- `ocr_pdf(input_path, output, lang, fmt, dpi)` — OCR a PDF page by page
- `make_searchable_pdf(input_path, output, lang, dpi)` — Embed text layer into scanned PDF
- `batch_ocr(directory, lang, fmt, recursive)` — Sequential batch (engine-level)

**Private helpers:**
- `_run_tesseract(image_path, lang)` — Thin wrapper around `pytesseract.image_to_string()`
- `_pdf_to_images(pdf_path, dpi)` — Converts PDF pages to PNGs in a temp dir via `pdf2image`
- `_write_output(text, path, fmt)` — Handles TXT / JSON / MD output format switching
- `_get_tesseract_cmd()` / `_get_poppler_path()` — Looks up saved tool paths from `config_manager`

**OCR pipeline for a PDF:**
```
_pdf_to_images()  →  preprocess_for_ocr()  →  _run_tesseract()  →  _write_output()
     ↑                      ↑                        ↑
 pdf2image             Pillow + OpenCV           pytesseract
 (Poppler)
```

**`make_searchable_pdf` — how it works:**
1. Convert each page to PIL image via `pdf2image.convert_from_path()`
2. Run `pytesseract.image_to_pdf_or_hocr(page, extension="pdf")` — this produces a PDF page with invisible text overlay
3. Merge all pages using `PdfWriter` from pypdf
4. Write final `.._searchable.pdf`

---

## `processor.py` — Image Preprocessing Pipeline

**Responsibility:** Prepare raw scans/images for OCR by fixing common degradation.

**Functions:**
- `preprocess_for_ocr(input_path)` — Full pipeline: enhance → deskew → denoise → returns temp PNG path
- `enhance(input_path)` — Pillow `ImageEnhance.Contrast` + `ImageEnhance.Sharpness`
- `deskew(input_path)` — OpenCV Hough line transform to detect skew angle, then rotate to correct
- `denoise(input_path)` — OpenCV `fastNlMeansDenoisingColored`
- `resize(input_path, width, height, percent)` — Pillow resize with aspect-ratio preservation
- `_load_pil(path)` / `_load_cv2(path)` / `_save_pil(img, path)` — internal I/O helpers

**Why preprocessing matters:** Raw scans fed directly to Tesseract produce poor results. Deskewing alone can improve OCR accuracy by 20-40% on tilted scans.

---

## `operations.py` — PDF & Image Operations

**Responsibility:** Core PDF manipulation (via pypdf) and image transformations (via Pillow/OpenCV).

**PDF operations:**
- `merge(files, output)` — `PdfWriter.append()` in a loop; validates each input exists first
- `split(input_path)` — One `PdfWriter` per page; outputs `original_page_001.pdf`, etc.
- `compress(input_path, preset)` — Ghostscript subprocess: `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/{preset}`
- `rotate(input_path, angle)` — `page.rotate(angle)` on each page via pypdf
- `extract_pages(input_path, page_range)` — Parses "1-5,7,9-11" range syntax, copies selected pages
- `watermark(input_path, watermark_path)` — `page.merge_page(watermark_reader.pages[0])`
- `encrypt(input_path, password)` — `PdfWriter.encrypt(password)`
- `decrypt(input_path, password)` — `PdfReader(password=…)` then rewrite without encryption

**Image operations (Pillow/OpenCV):**
- `enhance`, `deskew`, `denoise`, `resize_image`, `crop_image`, `rotate_image`
- `flip_horizontal`, `flip_vertical`, `convert_image`
- `compress_image` — Pillow save with `quality=` param
- `add_text_watermark` — PIL `ImageDraw.text()` with configurable position/color/opacity
- `remove_background` — `rembg.remove()` (requires `docmax[image]` extra)

**`merge` — most notable edge cases handled:**
- Each file validated for existence before opening
- Outputs a temp file first, then renames to avoid clobbering input if output path == one of the inputs
- Page count reported in success message

---

## `batch.py` — Parallel Batch Runner

**Responsibility:** Multi-threaded batch execution for OCR, compress, and convert over a directory.

**Core function — `_run_parallel(label, files, workers, handler)`:**
```python
def _run_parallel(label, files, workers, handler):
    errors = []
    worker_count = max(1, workers or 1)

    with Progress(...) as progress:
        task = progress.add_task(label, total=len(files))

        if worker_count == 1:
            # Sequential path — no threading overhead
            for path in files:
                try:
                    handler(path)
                except Exception as exc:
                    errors.append((path, str(exc)))
                progress.advance(task)
            return errors

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {executor.submit(handler, path): path for path in files}
            for future in as_completed(futures):
                path = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    errors.append((path, str(exc)))
                progress.advance(task)

    return errors
```

Key design points:
- **Graceful degradation:** `workers=1` takes the sequential path (no thread overhead, easier debugging)
- **Non-fatal errors:** Any file that fails is collected into `errors` list and reported at the end — one bad file doesn't abort the whole batch
- **`as_completed` ordering:** Progress bar updates as files finish, not in submission order — gives accurate real-time feedback
- **`handler` is a closure:** Each batch function (OCR/compress/convert) passes a local `def handler(path)` that captures the format/language params via closure

**Public batch functions:**
- `batch_with_ocr(directory, lang, fmt, recursive, workers)` — OCR all images + PDFs
- `batch_compress(directory, recursive, workers)` — Compress all PDFs
- `batch_convert(directory, target_format, recursive, workers)` — Convert all docs via Pandoc

---

## `watcher.py` — Directory Automation

**Responsibility:** Monitor a folder for new files and auto-process them.

**Classes:**
- `_DocMaxHandler` — Stores action/lang/fmt state and a `_seen: set` for deduplication. Method `dispatch(path)` routes each new file to the right operation.
- `_WatchdogBridge(FileSystemEventHandler)` — Adapter that maps watchdog's `on_created` / `on_moved` events to `handler_state.dispatch(path)`. Defined inline inside `watch()`.

**`watch()` function flow:**
1. Import watchdog (raises helpful error if not installed)
2. Create `_DocMaxHandler` with the requested action
3. Create `_WatchdogBridge` (inner class) that delegates to handler
4. Start `Observer`, schedule bridge on directory
5. `while True: time.sleep(1)` — blocks until Ctrl+C
6. On `KeyboardInterrupt`: `observer.stop()` → `observer.join()`

**Deduplication (why it exists):** Some OS file writers trigger both `on_created` AND `on_moved` events for the same file (write to temp, then rename). The `_seen: set` prevents double-processing.

**Debounce:** `time.sleep(WATCH_DEBOUNCE_SECONDS)` (default: 0.5s) is called inside `dispatch()` before processing, so files that are still being written are allowed to settle.

**Self-loop prevention:** Files output by DocMax itself (ending in `_searchable`, `_compressed`, `_ocr`, etc.) are explicitly ignored to prevent infinite processing loops.

---

## `converter.py` — Document Conversion

**Responsibility:** Format conversion via Pandoc subprocess and pdf2image/img2pdf.

**Functions:**
- `convert(input_path, target_fmt)` — Main entry. Calls Pandoc as subprocess: `pandoc input -o output`
- `images_to_pdf(paths_or_dir)` — Collects image files, calls `img2pdf.convert()` or Pillow fallback
- `pdf_to_images(input_path, dpi, fmt)` — `pdf2image.convert_from_path()` → saves each page as PNG/JPEG

**Format routing in `convert()`:**
```
Markdown → PDF:   pandoc input.md -o output.pdf --pdf-engine=xelatex
Markdown → DOCX:  pandoc input.md -o output.docx
DOCX → PDF:       pandoc input.docx -o output.pdf
DOCX → MD:        pandoc input.docx -o output.md
```

**Why subprocess for Pandoc:** Pandoc is a Haskell binary with no official Python binding. The `pypandoc` library exists but adds an extra dependency and version-lock risk. Direct subprocess gives full flag control.

---

## `extractor.py` — Content Extraction

**Responsibility:** Pull structured content out of PDFs.

**Functions:**
- `extract_text(input_path)` — `PdfReader.pages[i].extract_text()` concatenated
- `extract_images(input_path)` — Iterates `page["/Resources"]["/XObject"]`, saves embedded image objects
- `extract_metadata(input_path)` — `PdfReader.metadata` → normalized dict → JSON file
- `extract_tables(input_path, fmt)` — **Most complex function (cyclomatic complexity 16)**

**`extract_tables` internals:**
1. Opens PDF with `pdfplumber`
2. For each page, calls `page.extract_tables()`
3. Converts raw 2D list to pandas DataFrame (first row as header)
4. Handles blank cells, merged headers, and pages with no tables
5. Outputs to CSV (one file per table), XLSX (one sheet per table), or JSON

---

## `config_manager.py` — Persistent Config

**Responsibility:** Read/write `~/.docmax/config.json`. The single source of truth for tool paths and user preferences.

**Pattern used:** Every function calls `load_config()` (reads from disk), modifies the dict if needed, then calls `save_config()`. No in-memory caching — reads are cheap (JSON < 1KB).

```python
CONFIG_DIR  = Path.home() / ".docmax"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:          # read JSON, return {} on any error
def save_config(config: dict):      # mkdir parents, write JSON with indent=4
def get_tool_path(tool: str):       # load_config().get(f"tool_{tool}")
def set_tool_path(tool, path):      # load → update → save
def get_preference(key, default):   # load_config().get(f"pref_{key}", default)
def set_preference(key, value):     # load → update → save
def save_recent_folder(folder):     # load → update → save
def load_recent_folder():           # load_config().get("recent_folder")
```

**Why no caching:** The config is written by `setup.py` after tool discovery. If `engine.py` cached the value at import time, a freshly-installed Tesseract wouldn't be picked up until restart. Disk reads on every access avoids this stale-cache problem.

---

## `utils.py` — Shared Utilities

**Fan-in: 113** — the most-called module in the codebase.

Key functions:
- `abort(msg)` — Print error with `[red]` formatting, call `sys.exit(1)`. Called from 34 sites.
- `success(msg)` — Print with `[green]` formatting. Called from 27 sites.
- `info(msg)` — Print with `[cyan]` formatting. Called from 14 sites.
- `warn(msg)` — Print with `[yellow]` formatting.
- `ensure_parent(path)` — `path.parent.mkdir(parents=True, exist_ok=True)`. Called from 14 sites to prevent "No such file or directory" on output paths.
- `collect_files(directory, extensions, recursive)` — `Path.rglob("*")` filtered by extension set. Used by batch and watcher.
- `require_tesseract()` / `require_ghostscript()` / `require_pandoc()` — Check if tool is on PATH or in config; call `abort()` with install hint if missing.
