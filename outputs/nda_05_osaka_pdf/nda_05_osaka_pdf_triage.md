# Triage: nda_05_osaka_pdf.pdf

- **Document type:** nda
- **Priority:** medium
- **How standard:** 90% of the document matches our template
- **Needs a human:** YES - escalate
- **Deviations found:** 2 (0 not covered by playbook)
- **Analysis time:** 39s (backend: cli)

## Summary

Incoming mutual NDA with Osaka Digital KK is substantially our MNDA-2026 template. Two substantive deviations: two standard confidentiality carve-outs (independent development and legally-required disclosure) have been deleted from clause 3, and governing law/jurisdiction has been changed to Japan / Osaka District Court. The carve-out deletions are auto-redlined per NDA-CARVEOUTS. The governing-law change is outside our approved set and meets a DRAFT escalate_if under NDA-GOV-LAW, so a lawyer must own that point; escalating to human.

## Flagged deviations

### 3. Exclusions - REDLINE (playbook NDA-CARVEOUTS)

> (b) was known to the Recipient without restriction before disclosure; or (c) is rightfully received from a third party without a duty of confidentiality.

Two of the five standard carve-outs are missing: independent development and legally-required disclosure (with notice). Per NDA-CARVEOUTS all five are required; reinstate the deleted carve-outs verbatim from template clause 3. This is an auto-redline (escalate_if is a pushback condition only), so no escalation on the draft alone.

**Proposed text:** (b) was known to the Recipient without restriction before disclosure; (c) is independently developed by the Recipient without use of the Discloser's Confidential Information; (d) is rightfully received from a third party without a duty of confidentiality; or (e) is required to be disclosed by law or court order, provided the Recipient gives the Discloser prompt written notice where lawful and reasonable assistance to contest or limit the disclosure.

### 11. Governing Law - ESCALATE (playbook NDA-GOV-LAW)

> the laws of Japan, and the Osaka District Court shall have exclusive jurisdiction

Governing law/jurisdiction is Japan / Osaka District Court, outside our approved set (England and Wales, New York, Delaware, Ireland). This meets the DRAFT escalate_if in NDA-GOV-LAW, so a human must own this point. Opening position: revert to England and Wales.

**Proposed text:** the laws of England and Wales, and the courts of England shall have exclusive jurisdiction

## Estimated time

- Manual review baseline: ~25 min
- Review-only with this triage: ~14 min
- Estimated saving: ~11 min
