# Triage: nda_02_helios_term_govlaw.docx

- **Document type:** nda
- **Priority:** low
- **How standard:** 92% of the document matches our template
- **Needs a human:** No - all deviations covered by playbook
- **Deviations found:** 2 (0 not covered by playbook)
- **Analysis time:** 29s (backend: cli)

## Summary

Incoming mutual NDA closely follows our MNDA-2026 template with two substantive deviations: the term is extended to five (5) years (P6) and governing law/jurisdiction is New York rather than England and Wales (P12). The term is above our comment-only range but within the fallback, so it is auto-redlined to two years (NDA-TERM); New York is within our approved governing-law set, so it is acceptable as-is (NDA-GOV-LAW). No uncovered points and no DRAFT escalation triggers are met, so this does not require a lawyer.

## Flagged deviations

### 5. Term - REDLINE (playbook NDA-TERM)

> continues for a period of five (5) years

Term is five (5) years vs our standard two (2) years. Our comment-only range is 1-3 years, so this is outside acceptable-without-approval. Per NDA-TERM, revert to two (2) years as our opening position; up to five (5) years is acceptable under the fallback if the counterparty insists (confidentiality period stays within 5 years). Not an escalation as the term is not longer than 5 years or evergreen.

**Proposed text:** continues for a period of two (2) years

### 11. Governing Law - ACCEPT (playbook NDA-GOV-LAW)

> the laws of the State of New York, and the state and federal courts located in New York County shall have exclusive jurisdiction

Governing law/jurisdiction is New York rather than our standard England and Wales. New York is within our approved set (England and Wales, New York, Delaware, Ireland) per NDA-GOV-LAW, so this is acceptable without approval and within the escalate_if safe zone. Accept with no change.

## Estimated time

- Manual review baseline: ~25 min
- Review-only with this triage: ~9 min
- Estimated saving: ~16 min
