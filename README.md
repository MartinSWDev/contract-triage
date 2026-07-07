# Contract Triage Assistant

A playbook-driven triage-and-review assistant for a small in-house legal team
that processes a steady stream of low-stakes commercial contracts (mutual NDAs
and customer order forms). It reads an incoming contract (Word or PDF),
compares it clause-by-clause against the team's standard template and
playbook, auto-clears the boilerplate, and hands the lawyer:

1. a **redlined Word document** with real tracked changes and margin comments
   (the artefact they actually work in),
2. a **triage summary** (type, priority, how standard, what needs a human,
   estimated time saved),
3. **flagged deviations**, each carrying the team's pre-approved response —
   or an explicit **"NOT COVERED — needs a human"** flag when the playbook has
   no answer,
4. a **draft reply email** to the counterparty covering only the handled points.

The lawyer stays in control: every change arrives as a tracked change to
accept or reject, and every position cites the playbook rule it came from.

## Start here

| If you want to… | Read / open |
|---|---|
| See the app UI immediately (no build) | open [app/preview.html](app/preview.html) in a browser |
| See a finished result | open any `outputs/*/*_REDLINE.docx` in Word (e.g. `outputs/nda_03_quantix_heavy_redline/`) |
| Run the demo (CLI) | **Quick start** below |
| Build and run the real desktop app | [app/README.md](app/README.md) |
| See how I'd deliver this for real | [APPROACH.md](APPROACH.md) |
| See the measured results, failures included | [eval/REPORT.md](eval/REPORT.md) |
| Read the one-page plan written before building | [PLAN.md](PLAN.md) |

**Reviewing without running anything:** every output is pre-generated and
committed under `outputs/`, so you can open the redlined Word files, triage
summaries, and reply emails, browse `app/preview.html`, and read
`eval/REPORT.md` without installing anything or needing a Claude API key. You
only need credentials (below) to *re-run* the pipeline.

## The problem, in one paragraph

~80% of each contract is boilerplate the team has read hundreds of times, and
the redlines they receive are recurring ones with known answers. The cost is
attention, not judgment — finding the three clauses that changed and
remembering the standard response — and the queue backs up exactly when sales
spikes. A generic "summarise this contract" tool doesn't remove that work; a
playbook diff does. See [PLAN.md](PLAN.md) for the full framing.

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Regenerate templates + synthetic samples + ground truth (already included)
.venv/bin/python src/generate_documents.py

# Triage one contract
.venv/bin/python src/pipeline.py samples/nda_03_quantix_heavy_redline.docx

# Run everything + the evaluation
.venv/bin/python src/run_all.py
.venv/bin/python eval/evaluate.py     # writes eval/REPORT.md
```

**Credentials:** the assistant uses the Anthropic API (`claude-opus-4-8`) if
`ANTHROPIC_API_KEY` / `ANTHROPIC_AUTH_TOKEN` is set, and otherwise falls back
to the `claude` CLI in headless mode, reusing an existing Claude Code login.
Override with `TRIAGE_BACKEND=api|cli` and `TRIAGE_MODEL=<model-id>`.

## What's in the box

```
PLAN.md                 the one-page plan written before building
APPROACH.md             how this would be delivered for real (discovery, data,
                        RAG, the human-in-the-loop feedback loop, rollout)
playbook/playbook.yaml  standard positions, fallbacks, pre-approved redlines,
                        escalation triggers (NDA + order form)
templates/              the standard Mutual NDA and Order Form (.docx)
samples/                9 synthetic incoming contracts (.docx and .pdf)
samples/ground_truth/   per-sample expected results, generated with the samples
src/                    the assistant (ingest -> analyse -> verify -> redline)
app/                    optional native desktop dashboard (Tauri) — see app/README.md
outputs/                generated results for all 9 samples (redlines included)
eval/REPORT.md          the measured evaluation, failures kept in
```

### Optional: native desktop app

`app/` is a Tauri desktop dashboard over the same pipeline — point it at a
folder, run contracts, view each redline/summary/reply, and generate the
scorecard, all without the command line. It shells out to `src/app_api.py`, so
there is one copy of the logic. Run with `cd app/src-tauri && cargo tauri dev`
(needs Rust + `cargo install tauri-cli --version ^2`). Details in
[app/README.md](app/README.md). The CLI remains the primary interface; the app
is a convenience layer.

## How it works

```
contract.docx/.pdf
   │  ingest.py     extract paragraphs (pypdf re-segments PDFs on clause headings)
   ▼
analyzer.py         one Claude call: playbook YAML + both templates + numbered
   │                contract paragraphs -> strict-JSON analysis (doc type,
   │                triage fields, deviations w/ verbatim quotes + rule ids,
   │                draft reply)
   ▼
verify()            deterministic check: every quoted snippet must literally
   │                appear in the source text; unverifiable quotes are
   │                downgraded to comment-only and reported — a fabricated
   │                quote can never become a tracked change
   ▼
redline.py          word-level diff of snippet vs proposed text -> w:ins/w:del
   │                tracked changes + margin comments on the original .docx
   │                (PDFs are first re-materialised as .docx)
   ▼
pipeline.py         writes REDLINE.docx, triage.md, reply_email.md, analysis.json
```

## Key design decisions and why

- **The playbook is the product.** The model is never asked "what do you think
  of this clause?" — it is asked "which playbook rule covers this deviation,
  and what does that rule say?". Every suggestion cites a rule id, so a lawyer
  can audit any output back to a document their team owns. Updating behaviour
  means editing YAML, not prompts or code.
- **Honesty is enforced, not requested.** Deviations with no matching rule
  must be emitted as `covered: false` + "NOT COVERED — needs a human", and the
  eval scores "hallucinated advice on uncovered deviations" as its own metric
  (0 on the current run). A triage tool that guesses is worse than no tool.
- **Deterministic verification between the model and the document.** LLMs
  paraphrase; tracked changes need exact anchors. Every `original_snippet` is
  machine-checked against the source text before any XML is touched. On the
  current run, 0 unverified quotes reached an output.
- **Tracked changes, not a report about changes.** The deliverable is the
  `.docx` the lawyer would have produced by hand: minimal word-level
  `w:ins`/`w:del` runs, whole-clause strikes for delete-this-clause rules, and
  a margin comment per deviation explaining the playbook position.
- **Small, swappable LLM adapter.** `src/llm.py` is ~70 lines; API vs CLI is
  an env var. This is also the confidentiality seam (below).
- **No web UI, deliberately.** The lawyer's real surface is Word and email.
  A demo UI would have consumed the budget that went into redline quality and
  the eval. (The brief's Taste Skill instruction applies only if a UI is
  built.)

## Evaluation (measured, not asserted)

Full report with per-sample tables and commentary: [eval/REPORT.md](eval/REPORT.md).
Headlines from the included run over all 9 samples:

| Metric | Result |
|---|---|
| Document-type triage accuracy | 9/9 |
| Deviation recall / precision | 100% (15/15) / 100% (15/15) |
| Hallucinated advice on uncovered deviations | 0 |
| Unverified quotes in output | 0 |
| Escalation-flag accuracy | 9/9 |
| Mean analysis time | ~33s per contract |
| Estimated saving | ~12 min per contract → ~12 lawyer-hours/month at 60 contracts |

**Read these scores skeptically** — they are an upper bound on 9 synthetic
contracts written by the same author as the playbook, not production accuracy.
The first run scored escalation 6/9; investigating the three disagreements
found one real model gap (it under-escalated when a draft both crossed an
escalation trigger *and* had a pre-approved redline — fixed with a
disposition-precedence rule plus deterministic derivation of the doc-level
flag) and two genuine errors in my own playbook/ground truth (a Net-90 term the
model correctly escalated, and an uncovered deviation the model correctly
caught, both of which my labels had wrong). The full changelog and the
skeptical reading are in [eval/REPORT.md](eval/REPORT.md); the two label fixes
are annotated in `src/contract_texts.py`. Re-run the harness on 20–30
anonymised real contracts before trusting any of this.

## Honest limitations

- **Synthetic, well-behaved inputs.** Real paper has scanned PDFs (no OCR path
  here), reordered clauses, cross-references and defined terms spread across
  sections. The verbatim-quote verifier will survive that; recall numbers may not.
- **Escalation judgment is only as good as the playbook's wording** — see the
  eval commentary. Escalation triggers must be written as testable conditions
  on the incoming draft.
- **One LLM call per contract, no self-consistency.** A second adversarial
  "what did the first pass miss?" pass would likely raise recall on messy
  documents at ~2x cost.
- **Redline formatting fidelity is good but not perfect** on exotic documents
  (tables, numbered-list clauses); the fallback is always a comment-only flag,
  never a silent skip.
- **Time-saved figures are estimates** with stated assumptions, not
  measurements. Instrument the pilot (below) to replace them.

## Confidentiality

Contracts are confidential by definition. Three tiers, in order of preference:

1. **Default:** Anthropic API with zero-data-retention / no-training terms
   (standard on commercial API agreements) — appropriate for the low-stakes
   NDAs and order forms this tool targets.
2. **Sensitive matters:** route to a self-hosted or VPC model (e.g. Claude on
   AWS Bedrock inside the company's own cloud boundary, or a local
   open-weights model). The entire provider surface is `src/llm.py`; swapping
   backends is a one-file change and could be driven by the triage itself
   (e.g. any contract mentioning M&A terms never leaves the network).
3. **Never index or retain:** the pipeline is stateless — nothing is stored
   outside the `outputs/` folder the team controls.

## Introducing it to the team, and handing it over

**Rollout (shadow → assist → trust):**
1. *Shadow (2 weeks):* run the assistant on every incoming contract but
   lawyers review as they do today; compare notes weekly. This doubles as the
   real-world eval — every disagreement is either a playbook edit or a logged
   model failure.
2. *Assist:* lawyers start from the redline for the two covered contract
   types; anything flagged "not covered" or escalated goes through the old
   path. Track accept-rate of proposed redlines per rule id.
3. *Trust selectively:* rules with sustained ~100% accept-rate (e.g. governing
   law swaps) can be batched for one-click approval. Full auto-send is
   deliberately out of scope.

**Handover so it keeps running:**
- The playbook is YAML owned by the legal team, with rule ids and a
  `last_reviewed` date; editing it requires no engineering. A quarterly
  15-minute review against the "not covered" log is the maintenance loop —
  every recurring uncovered deviation is a new rule waiting to be written.
- The eval harness is the regression test: after any playbook or model change,
  `run_all.py && evaluate.py` re-scores the whole sample set in ~10 minutes.
  New failure cases from live use should be added to `samples/` with ground
  truth, growing the test set over time.
- Total surface: ~800 lines of commented Python, five modules, one prompt,
  no framework. Any developer (or a capable coding agent) can maintain it.
