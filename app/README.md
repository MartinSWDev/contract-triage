# Contract Triage — desktop app (Tauri)

A native desktop dashboard over the same Python pipeline. Point it at a folder
of contracts, run them, view each redline/summary/reply, and produce the
evaluation scorecard — without touching the command line.

It is a thin shell: the Rust backend (`src-tauri/src/main.rs`) shells out to
`../src/app_api.py` in the project venv for every action, so there is exactly
one copy of the analysis logic. Nothing is reimplemented in Rust.

## What it does

- **Browse folder / read from a location** — native folder picker (defaults to
  the project's `samples/`).
- **Table of contracts** — type, priority, deviation count (with a red
  "not covered" pill), outcome (auto-cleared vs needs-human), estimated minutes
  saved, and analysis time.
- **Run** one contract or **Run all pending** — each calls Claude via the
  pipeline (~30–60s each) and refreshes the row.
- **View** — a detail drawer with the triage summary, every flagged deviation
  (disposition badge, playbook rule id, verbatim quote, proposed text, comment),
  the draft reply, and the path to the tracked-changes Word file.
- **Score all (eval)** — runs the evaluator and shows the scorecard (triage,
  escalation, precision, recall, hallucinated-advice and unverified-quote
  counts, mean time, minutes saved).

## See it without building anything

Open [preview.html](preview.html) in any browser. It's the real UI with sample
data baked in — you can click through the contract list, open the detail drawer
for each one, and see the scorecard. Buttons that need the OS (open file, folder
picker, running contracts) are stubbed in the static preview; build the app
below to run it live.

## Prerequisites

- The Python venv set up per the top-level README (`.venv/` with deps).
- Rust (1.77+) and the Tauri CLI:
  ```bash
  cargo install tauri-cli --version '^2'
  ```
  (Node is only needed if you later add a JS build step; the frontend here is
  plain static HTML, so none is required.)

## Run it

```bash
cd app/src-tauri
cargo tauri dev          # opens the native window
```

To produce a distributable bundle (.app / .dmg on macOS):

```bash
cargo tauri build
```

The backend resolves the project root from the crate location, so run it from
the repo checkout. To point at a different Python, set `TRIAGE_PYTHON`.

## Notes

- The frontend was designed with the `design-taste-frontend` skill's anti-slop
  directives applied: a cool near-monochrome palette with a single saturated
  orange accent (deliberately **not** the warm cream/oxblood/espresso
  "AI premium-craft" palette the skill flags as a top AI-tell), a locked radius
  scale, tactile button states, and serif type reserved for exactly one place —
  the verbatim contract quotes — where it meaningfully echoes the document
  rather than decorating the UI.
- The Rust `target/` build directory is excluded from the delivered zip; the
  first `cargo build`/`cargo tauri dev` regenerates it (~15s after crates are
  cached; a few minutes on the very first fetch).
- GUI window-open is verified on a normal desktop; in a headless build only the
  compile + the Python command layer can be checked, both of which pass.
