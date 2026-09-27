# 05 — Complex Functions & Algorithms

> Load this for: deep-dive coding rounds, "explain your most complex piece of code", complexity analysis questions.

---

## Complexity leaderboard (cyclomatic complexity)

| Rank | Function | File | Cyclomatic | Cognitive | Loop depth |
|---|---|---|---|---|---|
| 1 | `extract_tables` | extractor.py | 16 | 35 | 2 |
| 2 | `main` | cli.py | 14 | 45 | 1 |
| 3 | `merge_workflow` | workflows/pdf.py | 13 | 16 | 1 |
| 4 | `make_searchable_pdf` | engine.py | 12 | 16 | 2 |
| 5 | `setup_dependencies` | setup.py | 10 | 26 | 0 |
| 6 | `_run_parallel` | batch.py | 9 | 29 | 1 |
| 7 | `images_to_pdf` | converter.py | 9 | 16 | 1 |
| 8 | `batch_ocr` | engine.py | 9 | 19 | 1 |
| 9 | `extract_images` | extractor.py | 9 | 17 | 2 |
| 10 | `_discover_tool` | setup.py | 9 | 27 | 4 |

---

## `extract_tables` — complexity 16, cognitive 35

This is the most complex function. It deals with the chaotic reality of PDF table structure.

**Why it's complex:**
- PDF tables have no standard schema — `pdfplumber` returns raw 2D lists where cells may be `None`, empty strings, or merged
- Must handle: pages with no tables, tables with no headers, tables where the "header" row is all empty, multi-sheet XLSX output, single-file vs. per-table CSV output
- Format branching: CSV, XLSX, JSON each need different output logic

**Simplified logic:**
```python
def extract_tables(input_path, fmt):
    import pdfplumber, pandas as pd
    all_tables = []

    with pdfplumber.open(input_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()           # raw 2D lists
            for table in tables:
                if not table or len(table) < 2:      # skip empty/headerless
                    continue
                df = pd.DataFrame(table[1:], columns=table[0])  # first row = header
                df = df.fillna("")                   # replace None with ""
                all_tables.append((page_num, df))

    if not all_tables:
        abort("No tables found in PDF")

    if fmt == "csv":
        for i, (page, df) in enumerate(all_tables):
            df.to_csv(output_stem / f"table_{i+1}.csv", index=False)
    elif fmt == "xlsx":
        with pd.ExcelWriter(output) as writer:
            for i, (page, df) in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f"Table_{i+1}", index=False)
    elif fmt == "json":
        data = [{"page": p, "data": df.to_dict("records")} for p, df in all_tables]
        output.write_text(json.dumps(data, indent=2))
```

**Interview talking point:** The nested loops (page → tables per page) combined with the 3-way format branch is what drives the cyclomatic complexity. A cleaner design would separate extraction from serialization — `extract_tables_raw()` returns a list of DataFrames, and a separate `serialize_tables(tables, fmt)` handles output. I'd refactor it that way if adding a new format.

---

## `make_searchable_pdf` — complexity 12

**What it does:** Takes a scanned (image-only) PDF and produces a new PDF where the original page image is preserved but invisible OCR text is overlaid, making it searchable with Ctrl+F.

**Algorithm:**
```
for each page:
    1. pdf2image.convert_from_path() → PIL Image
    2. pytesseract.image_to_pdf_or_hocr(image, extension="pdf")
       → returns bytes of a PDF page with the original image + invisible text layer
    3. Collect all page bytes

merge all page PDFs:
    PdfWriter + PdfReader(io.BytesIO(page_bytes)) for each page
    writer.add_page(reader.pages[0])

write final PDF
```

**Key insight:** `pytesseract.image_to_pdf_or_hocr()` does both OCR and PDF embedding in one call. It uses Tesseract's built-in `pdf` output mode (HOCR under the hood) which places text characters at the exact pixel coordinates of the recognized words. The original image is the visible layer; the text is invisible but selectable.

**Why two separate libraries for PDF pages:** `pdf2image` (Poppler-based) is more accurate for rendering PDF pages to images than pypdf's built-in rendering. pypdf is used for the final merge because it's already a dependency and handles `PdfWriter` cleanly.

---

## `_run_parallel` — complexity 9, cognitive 29

Already covered in `03-key-modules.md`. Key complexity driver: the dual sequential/parallel path + `as_completed` iteration + error collection inside the progress context manager.

**Time complexity:** O(n) where n = number of files. Each file is processed once. The thread pool adds a constant scheduling overhead per file.

**Space complexity:** O(n) for the `futures` dict (maps Future → Path for all submitted jobs).

---

## `_discover_tool` in `setup.py` — complexity 9, loop depth 4

This is the tool auto-discovery function — given a tool name (e.g., "tesseract"), it finds the binary on the system.

**Search strategy (in order):**
1. Check if it's already on `PATH` (`shutil.which(tool)`)
2. Search common OS-specific install directories (hardcoded list per OS)
3. Walk those directories recursively looking for the binary name
4. On Windows: also search `Program Files`, `Program Files (x86)`, `Chocolatey`, `Scoop`
5. If found, save the path to `config_manager.set_tool_path(tool, path)`

**Why loop depth 4:** Outer loop over search dirs → `os.walk()` generates (root, dirs, files) triples → loop over files → string comparison. This is unavoidable for recursive filesystem search.

**Interview talking point:** An alternative would be using OS package manager query commands (`which tesseract`, `where tesseract`, `brew --prefix tesseract`) and only falling back to filesystem walk. That would be faster but less reliable on non-standard installs.

---

## `watch()` + `_DocMaxHandler.dispatch()` — complexity 8+

The interaction between `watch()`, `_WatchdogBridge`, and `_DocMaxHandler` involves three classes and two levels of delegation:

```
watchdog Observer
    └─ schedules _WatchdogBridge (extends FileSystemEventHandler)
         └─ on_created / on_moved → calls handler_state.dispatch(path)
              └─ _DocMaxHandler.dispatch(path)
                   ├─ dedup check (_seen set)
                   ├─ debounce sleep
                   ├─ suffix filtering (ignore DocMax-generated files)
                   ├─ extension filtering (only process supported exts)
                   └─ late-import + route to correct engine function
```

**Why `_WatchdogBridge` is an inner class defined inside `watch()`:** It needs to close over `handler_state` (the `_DocMaxHandler` instance). Defining it inside `watch()` means no need to pass `handler_state` as a constructor arg or store it as a class attribute — the closure handles it cleanly.

---

## `merge_workflow` — complexity 13

`merge_workflow` in `workflows/pdf.py` has high complexity because it handles:
- Multi-file selection (Questionary `checkbox` prompt)
- File ordering (user can reorder selected files)
- Output path selection (default suggestion + override)
- Validation (at least 2 files selected)
- Calling `merge()` and reporting result

It's complex because it's coordinating a lot of user interaction, not because of algorithmic complexity. The cyclomatic score is high from the number of conditional branches checking user input validity.

---

## OCR pipeline: end-to-end time complexity

For a k-page PDF with average image size n pixels:

| Step | Complexity |
|---|---|
| `_pdf_to_images` | O(k) — one subprocess call, renders k pages |
| `preprocess_for_ocr` per page | O(n) — pixel-wise operations |
| `_run_tesseract` per page | O(n log n) approx — Tesseract's internal pipeline |
| `_write_output` | O(w) where w = word count |
| **Total** | **O(k × n log n)** |

For batch with p files: O(p × k × n log n) sequential, O((p/workers) × k × n log n) parallel.

---

## Hotspot functions by call frequency

| Function | Fan-in (callers) | Role |
|---|---|---|
| `abort()` | 34 | Universal error exit |
| `success_screen()` | 30 | TUI success display |
| `success()` | 27 | Console success message |
| `get_output_name()` | 20 | Derive output filename |
| `info()` | 14 | Console info message |
| `ensure_parent()` | 14 | Create parent dirs |
| `failure_screen()` | 12 | TUI failure display |
| `select_single_pdf()` | 12 | File picker prompt |
| `get_tool_path()` | 12 | Config lookup |
| `convert()` | 11 | Pandoc conversion |

`abort()` being called from 34 sites reflects the defensive programming style throughout — every function validates its inputs immediately and exits cleanly with a message rather than letting errors propagate as uncaught exceptions.
