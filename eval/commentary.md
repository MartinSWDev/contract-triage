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
