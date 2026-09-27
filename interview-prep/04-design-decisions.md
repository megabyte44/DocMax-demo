# 04 — Design Decisions & Tradeoffs

> Load this for: "Why did you choose X?", "What tradeoffs did you consider?", "How would you scale this?", "What would you do differently?"

---

## Why Typer + Questionary (not Click or argparse)?

**Typer** was chosen over Click/argparse because:
- Automatic `--help` generation from Python type hints and docstrings
- Built-in Typer `Option`/`Argument` with sensible defaults and validation
- No manual argument registration boilerplate — just annotate the function

**Questionary** was chosen for the interactive TUI because:
- Clean, minimal API: `questionary.select()`, `questionary.text()`, `questionary.path()`
- Works well with Rich for consistent styling
- Alternative: `InquirerPy` (heavier) or raw `prompt_toolkit` (too low-level)

**Both together:** `cli.py` uses Typer for the subcommand interface; `menu.py` + `workflows/` use Questionary for the guided TUI. Same core functions power both paths — no duplication.

---

## Why the Workflow layer exists

Without a workflow layer, either:
1. CLI subcommands contain TUI prompting logic (can't call them cleanly from scripts), OR
2. TUI functions re-implement the core logic (duplication + divergence bugs)

The workflow layer (`workflows/*.py`) is the bridge: it prompts for missing params, then calls the same core function that the CLI subcommand calls. This is a variant of the **Command pattern** — the core function is the command; the workflow wraps it for interactive use.

---

## Why `ThreadPoolExecutor` over `ProcessPoolExecutor`

The batch operations are predominantly **I/O-bound:**
- OCR: subprocess call to Tesseract (I/O wait) + file read/write
- Compression: subprocess call to Ghostscript (I/O wait) + file write
- Conversion: subprocess call to Pandoc (I/O wait) + file write

Python's GIL doesn't block threads waiting for subprocess exit or file I/O. `ThreadPoolExecutor` works correctly here and avoids multiprocessing's serialization (pickling) overhead for the handler closures.

**Tradeoff:** If someone adds CPU-bound processing (e.g., pure-Python image transforms), threads would start contending on the GIL. The fix would be switching to `ProcessPoolExecutor` for those specific handlers — the `_run_parallel` abstraction makes this a local change.

---

## Why subprocess for Ghostscript and Pandoc

Both Ghostscript and Pandoc are external binaries:
- **Ghostscript:** No stable, maintained Python binding. `ghostscript` PyPI package exists but is unmaintained. The CLI is the stable interface.
- **Pandoc:** Haskell binary. `pypandoc` exists but ties you to a specific Pandoc version and adds install complexity. Direct subprocess gives full flag access.

**Tradeoff:** Subprocess means Ghostscript/Pandoc must be installed separately. This is handled by `docmax setup` (auto-installer) and `docmax doctor` (health checker) so users aren't left guessing.

---

## Offline-first design

Every operation runs locally. No API keys, no cloud upload, no internet check. This was a hard requirement because:
1. Document processing often involves sensitive files (invoices, contracts, medical records)
2. Offline tools are faster (no upload/download round-trip)
3. No rate limits, no pricing tiers, no account needed

**Tradeoff:** More complex installation (external tool dependencies) compared to a cloud-backed tool that wraps an API.

---

## Optional extras instead of one fat install

```toml
[project.optional-dependencies]
ocr    = ["pytesseract", "pdf2image", "Pillow"]
image  = ["opencv-python", "rembg", "Pillow"]
tables = ["pdfplumber", "pandas", "openpyxl"]
full   = [all of the above]
```

**Why:** `opencv-python` (~50MB), `rembg` (~200MB with model weights), and `pandas+openpyxl` are heavy. A user who only needs PDF merge/split shouldn't pull them in. Optional extras let the base `pip install docmax` stay under 10MB.

**Tradeoff:** If a user runs a command that needs a missing extra, they get a clear import error with install instructions (handled by `abort()` messages in each function that does a late import).

---

## Config as flat JSON (no SQLite, no TOML)

`~/.docmax/config.json` stores tool paths and preferences. Alternatives considered:
- **SQLite:** Overkill for ~5 key-value pairs. Adds `sqlite3` dependency complexity.
- **TOML:** Good choice, but `tomllib` (stdlib) is read-only; writes need `tomli-w` or `tomlkit`. JSON is read/write with just the stdlib.
- **Platform-specific registry/plist:** Not cross-platform.

**Pattern:** Every read calls `load_config()` from disk (no in-memory cache). Rationale: the config is small (<1KB), and caching would cause stale-path bugs after `docmax setup` updates a tool path mid-session.

---

## Watcher debounce and deduplication

Two separate mechanisms prevent double-processing in watch mode:

1. **`_seen: set`** — Added before any sleep. Prevents the same path from being dispatched twice if both `on_created` and `on_moved` fire.
2. **`time.sleep(WATCH_DEBOUNCE_SECONDS)`** — Added inside `dispatch()` before processing. Lets the file writer finish before DocMax opens the file. Without this, OCR on a file that's still being written produces garbage output.

**Why not a proper debounce timer (e.g., threading.Timer)?** A fixed sleep is simpler and sufficient — document files are rarely large enough that the write takes more than 0.5 seconds. A proper debounce timer would add complexity for marginal benefit.

---

## Self-loop prevention in watcher

Output files are named with known suffixes (`_searchable`, `_compressed`, `_ocr`, etc.). The watcher explicitly checks `path.stem.endswith(suffix)` and skips these files. Without this, processing `scan.pdf` would create `scan_searchable.pdf`, which would trigger another watch event, creating `scan_searchable_searchable.pdf`, ad infinitum.

---

## What I'd do differently at scale

1. **Add async support for the OCR engine** — `asyncio.subprocess` would allow more concurrency without thread overhead for the subprocess-heavy OCR path.
2. **Plugin system for operations** — Currently, adding a new operation requires editing `cli.py`, `menu.py`, and writing a workflow. A plugin registry pattern (e.g., decorator-registered operations) would make this extensible.
3. **Cache config in memory** — With a proper `invalidation-on-write` pattern (`save_config` clears the cache), the disk-per-call pattern could be replaced for lower latency.
4. **Structured logging** — `utils.py` currently prints to stdout. In a production CLI tool, a `--verbose` flag routing to `logging.DEBUG` would help with debugging user-reported issues.
5. **Progress reporting via callbacks** — The current Rich `Progress` bar is tightly coupled to the engine functions. A callback-based progress API would allow the same functions to be used headlessly (e.g., in tests or by a GUI wrapper).
