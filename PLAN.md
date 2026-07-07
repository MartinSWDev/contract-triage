# PLAN — Playbook-driven contract triage & review assistant

## My read of the problem

A small in-house legal team hand-reads a queue of low-stakes, highly repetitive
contracts (mutual NDAs, small order forms). ~80% of every document is boilerplate
they have read hundreds of times; the deviations they receive are mostly
*recurring* deviations with *known* answers. The cost is not legal judgment —
it is attention: finding the 3 clauses in a 12-clause document that actually
changed, and remembering what the team's standard answer is. The queue backs up
precisely when it matters most (end of month/quarter).

That shape — high-volume, low-variance, known-answer — is the best possible
case for an agentic assistant, and the worst possible case for a generic
"summarise this contract" tool. A summary still makes the lawyer read
everything. What removes work is **triage against a playbook**: auto-clear what
matches the standard, surface only what deviates, and pre-draft the team's own
known response for each deviation. The lawyer's job collapses from "read 12
pages" to "approve/adjust 4 pre-analysed decisions".

The single most important design rule: **the tool must know what it doesn't
know.** A deviation the playbook doesn't cover must be flagged "not covered —
needs a human", never papered over with a plausible-sounding suggestion. A
triage tool that silently guesses is worse than no tool.

## What I will build

1. **Playbook** (`playbook/playbook.yaml`): for NDAs and order forms — the
   team's standard position per clause topic, acceptable ranges, fallback
   positions, and pre-approved redline language for the common counterparty
   asks (liability caps, term, governing law, confidentiality carve-outs,
   non-solicit, auto-renewal, payment terms, etc.), plus explicit
   escalation triggers.
2. **Templates**: the company's standard mutual NDA and order form (`.docx`),
   the baseline the diff runs against.
3. **Samples**: 9 synthetic incoming contracts (`.docx` + a couple of PDFs to
   prove PDF ingest) with a graded spread: near-standard, common playbook-covered
   deviations, deviations the playbook deliberately does *not* cover
   (e.g. an IP assignment clause smuggled into an NDA, an unusual indemnity),
   and one out-of-scope document type. Each sample ships with a hand-written
   ground-truth file (`samples/ground_truth/*.yaml`) for the eval.
4. **Assistant** (`src/`): a pipeline that
   - ingests `.docx` or `.pdf`,
   - triages (contract type, priority, % standard) and diffs clause-by-clause
     against template + playbook using Claude with structured output,
   - deterministically **verifies every quote** the model returns against the
     source text (no fabricated deviations survive),
   - emits: a **redlined `.docx` with real tracked changes (w:ins/w:del) and
     margin comments** (the artefact the lawyer actually opens), a triage
     summary, a flagged-deviations report with playbook responses or
     "NOT COVERED — needs a human", and a draft reply email covering only the
     handled points.
   - LLM backend: Anthropic API if `ANTHROPIC_API_KEY` is set; otherwise the
     `claude` CLI in headless mode (which also gives a free path to "route
     sensitive contracts to a non-cloud backend": the adapter is one file).
5. **Evaluation** (`eval/`): run the assistant over all 9 samples ×
   ground truth; report triage accuracy, deviation precision/recall,
   playbook-response correctness, honesty on not-covered items (did it
   escalate or hallucinate an answer?), and a defensible time-saved estimate
   with stated assumptions. Failure cases stay in the report.

## What I am deliberately leaving out

- **No web UI.** The lawyer's real surface is Word + email; a demo UI would be
  polish, not function. The CLI + generated artefacts are the product.
- **No clause-library learning loop** (updating the playbook from accepted
  edits) — described in README as the obvious next step, not built.
- **No e-signature / CLM / inbox integration** — out of scope for a prototype.
- **No fine-tuning or embeddings index** — at this volume, a good playbook in
  the prompt beats retrieval infrastructure.

## How I will evaluate it (before building, so I can't move the goalposts)

- **Triage accuracy**: contract type + escalation tier vs ground truth.
- **Deviation detection**: precision & recall per contract, micro-averaged,
  matched on clause topic. A "caught" deviation must identify the right clause.
- **Playbook mapping**: for covered deviations, did it propose the playbook
  response (correct / wrong-but-safe / wrong-and-risky)?
- **Honesty**: for the deliberately-uncovered deviations, did it say "not
  covered" (pass) or invent advice (fail)? This is scored separately because
  it is the trust-critical metric.
- **Time saved**: measured processing time per contract, plus an estimate of
  lawyer minutes saved using stated (conservative, cited-in-report)
  assumptions of 25 min/contract manual vs review-only time; scaled to a
  60-contract month. Reported as an estimate, not a fact.

Success bar for the prototype: ≥90% correct triage, ≥85% deviation recall,
zero hallucinated playbook answers on the not-covered set. If it misses that
bar, the eval report says so.
