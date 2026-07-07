# Evaluation report

Run over 9 synthetic contracts (2 clean, 5 with playbook-covered deviations, 2 containing deviations the playbook deliberately does not cover, 1 out-of-scope document). Ground truth is defined next to the sample generator so it cannot drift from the documents. Metrics are computed by `eval/evaluate.py`; nothing below is hand-asserted.

## Headline metrics

| Metric | Result |
|---|---|
| Document-type triage accuracy | 100% (9/9) |
| Escalation decision accuracy | 100% (9/9) |
| Deviation recall | 100% (15/15) |
| Deviation precision | 100% (15/15) |
| Hallucinated advice on uncovered deviations | 0 |
| Unverified quotes that reached output | 0 |
| Mean analysis time per contract | 30s |

## Per-sample results

| Sample | Type OK | Escalation OK | Caught | Missed | False pos | Time |
|---|---|---|---|---|---|---|
| misc_09_offer_letter.docx | Y | Y | 0/0 | 0 | 0 | 13.9s |
| nda_01_borealis_clean.docx | Y | Y | 0/0 | 0 | 0 | 15.7s |
| nda_02_helios_term_govlaw.docx | Y | Y | 2/2 | 0 | 0 | 29.5s |
| nda_03_quantix_heavy_redline.docx | Y | Y | 3/3 | 0 | 0 | 37.6s |
| nda_04_vantage_ip_grab.docx | Y | Y | 2/2 | 0 | 0 | 27.8s |
| nda_05_osaka_pdf.pdf | Y | Y | 2/2 | 0 | 0 | 38.9s |
| of_01_atlas_clean.docx | Y | Y | 0/0 | 0 | 0 | 25.2s |
| of_02_northwind_payment_liability.docx | Y | Y | 4/4 | 0 | 0 | 46.8s |
| of_03_zephyr_uncapped_mfn.pdf | Y | Y | 2/2 | 0 | 0 | 37.4s |

## Failures and disagreements (kept, per the brief)

- None recorded on this run.

## Reviewer commentary (hand-written; metrics above are computed, not adjusted)

### Read the perfect scores skeptically

This run scores 9/9 on triage, escalation, precision and recall. That is an
**upper bound on a favourable test set**, not evidence of production accuracy:
9 synthetic contracts, written by the same person as the playbook, with clean
clause structure. Real counterparty paper (scanned PDFs, reordered clauses,
definitions split across sections, novel drafting) will be harder. The honest
claim is "the mechanism is sound and the trust properties hold", not "it is
93% accurate in the wild". Re-run this harness on 20-30 anonymised real
contracts before trusting the numbers.

### What changed between run 1 (escalation 6/9) and this run (9/9)

The first run exposed three escalation disagreements. Investigating each showed
two were product/label bugs and one was a real model gap:

1. **Real model gap (nda_03, nda_05).** Both deviations hit a rule's
   `escalate_if` trigger *on the incoming draft* (a 2-year non-solicit exceeds
   the 12-month ceiling; Japanese governing law is outside the approved list)
   but also had a pre-approved redline. The model picked "redline" and missed
   that escalation also fired. Fixed by (a) a disposition-precedence rule in
   the prompt - a draft-level `escalate_if` wins even when a redline exists,
   (b) rewording each `escalate_if` in the playbook to state plainly whether it
   is a DRAFT condition (fires now) or a PUSHBACK condition (fires only after
   the counterparty resists our redline), and (c) deriving the document-level
   escalation flag deterministically from the per-deviation dispositions so the
   two can never disagree.

2. **My playbook was internally inconsistent (of_02).** The Net-90 payment term
   is beyond the Net-60 fallback ceiling, so OF-PAYMENT's own `escalate_if`
   should fire - yet my first ground truth labelled of_02 non-escalating. The
   assistant escalated it, correctly. I fixed the ground-truth label.

3. **My ground truth missed a real deviation (of_02).** The sample deletes the
   late-payment-interest sentence; the playbook has no rule for it. The
   assistant flagged it "NOT COVERED - needs a human" - the right behaviour -
   and my first ground truth simply hadn't recorded it, so it scored as a false
   positive. I added it to the ground truth.

Points 2 and 3 mean I edited ground truth after seeing results. That is only
legitimate because the edits fix demonstrable errors (an incoherent rule and a
missed deviation that are objective facts about documents I generated), not
because they flatter the model. Both edits are called out in
`src/contract_texts.py` next to the sample. The prompt/playbook changes in
point 1 are genuine improvements that would help on unseen contracts too.

### The properties that actually matter held on both runs

- **0 hallucinated positions on uncovered deviations.** Every deviation with no
  playbook rule (IP-assignment grab, MFN clause, late-payment interest) was
  escalated, never given invented advice.
- **0 unverified quotes reached a tracked change.** Every snippet placed into
  the redline was machine-checked verbatim against the source document first.

These, not the headline accuracy, are what make the tool safe to put in front
of a lawyer.

## Time-saved estimate (assumptions stated, not measured)

This is an *estimate*, not a measurement - no lawyer timed themselves for this prototype. Assumptions:

- Manual baseline: 25 min per NDA/order form (industry surveys commonly cite 20-40 min for routine NDA review; 25 is deliberately conservative), 5 min to recognise and reroute an out-of-scope document.
- Assisted review: 5 min to read the triage summary and skim the redline, +2 min per flagged deviation, +5 min if escalation is needed.
- The assistant's own runtime is excluded (it runs before the lawyer opens the file).

| | |
|---|---|
| Mean saving per contract | ~12 min |
| Monthly volume assumed | 60 contracts |
| Estimated monthly saving | ~12 lawyer-hours |
| At GBP 150/h fully loaded | ~GBP 1,800/month |

The bigger operational win is queue latency: triage output is ready in ~30s, so clean contracts can turn around same-hour instead of waiting a day-plus in the queue.

## Reading the numbers honestly

- n=9 synthetic contracts written by the same author as the playbook. Real counterparty paper is messier: scanned PDFs, reordered clauses, definitions split across sections. Treat these numbers as an upper bound and re-run this eval on 20-30 anonymised real contracts before trusting it.
- The eval matches deviations by playbook rule id, so a deviation caught under the *wrong* rule would score as a miss plus a false positive - strict by design.
- 'Hallucinated advice on uncovered deviations' is the metric that matters most for trust: it counts cases where the playbook had no answer and the assistant invented one instead of escalating.
