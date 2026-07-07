# Triage: of_03_zephyr_uncapped_mfn.pdf

- **Document type:** order_form
- **Priority:** high
- **How standard:** 85% of the document matches our template
- **Needs a human:** YES - escalate
- **Deviations found:** 2 (1 not covered by playbook)
- **Analysis time:** 37s (backend: cli)

## Summary

This is a customer Order Form under MSA-2026 and is substantively standard except for two points. Clause 7 makes Provider's liability unlimited (uncapped) - a DRAFT escalate_if trigger under OF-LIABILITY-CAP, so it escalates even though a redline exists. Clause 3 adds a Most Favoured Customer/most-favoured-nation obligation that has no playbook rule and is NOT COVERED. Route to a lawyer.

## Flagged deviations

### 3. Most Favoured Customer - ESCALATE (NOT COVERED - needs a human)

> Provider represents and warrants that the fees and terms offered to Customer are no less favourable than those offered to any other customer of Provider, and shall extend to Customer and its affiliates any more favourable fees or terms offered to any other customer during the Subscription Term.

NOT COVERED - needs a human. Added most-favoured-customer/most-favoured-nation clause with a fee-and-terms warranty and automatic extension to affiliates. There is no playbook rule addressing MFN obligations; do not take a position - route to a lawyer.

### 7. Limitation of Liability - ESCALATE (playbook OF-LIABILITY-CAP)

> Notwithstanding anything in the MSA, Provider's liability arising out of or in connection with this Order Form shall be unlimited.

Provider's liability is made unlimited/uncapped. OF-LIABILITY-CAP escalate_if fires on 'Uncapped liability' - this is a DRAFT trigger, so it escalates now even though a redline exists. Opening position: restore the mutual 12 months' fees cap (up to 2x acceptable without approval; 3x super-cap only for confidentiality and data-protection breaches). A human must own the negotiation.

**Proposed text:** Subject to the exclusions in the MSA, each party's total aggregate liability arising out of or in connection with this Order Form is limited to the fees paid or payable by Customer under this Order Form in the twelve (12) months preceding the event giving rise to the claim.

## Estimated time

- Manual review baseline: ~25 min
- Review-only with this triage: ~14 min
- Estimated saving: ~11 min
