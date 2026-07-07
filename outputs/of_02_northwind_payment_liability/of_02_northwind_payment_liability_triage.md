# Triage: of_02_northwind_payment_liability.docx

- **Document type:** order_form
- **Priority:** high
- **How standard:** 80% of the document matches our template
- **Needs a human:** YES - escalate
- **Deviations found:** 4 (1 not covered by playbook)
- **Analysis time:** 47s (backend: cli)

## Summary

Customer order form (Northwind Retail Group) under MSA-2026. Three substantive deviations: payment extended to Net 90 (beyond our Net 60 ceiling - escalates), a general liability cap raised to 3x (above the 2x auto-approve limit - auto-redline to 2x), and auto-renewal removed (acceptable as-is). Draft also deletes late-payment interest, which is not covered by the playbook and needs a human. Escalation required.

## Flagged deviations

### Payment Terms - ESCALATE (playbook OF-PAYMENT)

> payable within ninety (90) days of the invoice date

OF-PAYMENT: standard is Net 30, acceptable to Net 45, fallback Net 60 for ACV >= 50,000 (this order is GBP 180,000). Net 90 is beyond Net 60, which meets the DRAFT escalate_if - a human must own this. Opening position is to revert to Net 60.

**Proposed text:** payable within sixty (60) days of the invoice date

### Payment Terms - ESCALATE (NOT COVERED - needs a human)

> No interest shall accrue on late amounts.

NOT COVERED - needs a human. The draft deletes the template's late-payment interest (4% above base rate) and states no interest accrues. The playbook has no position on late-payment interest, so this must be reviewed by a lawyer.

### Term and Renewal - ACCEPT (playbook OF-AUTORENEW)

> This Order Form does not renew automatically; any renewal shall be by written agreement of the parties.

OF-AUTORENEW: removal of auto-renewal (renewal by mutual agreement) is acceptable without approval. No change needed - comment only.

### Limitation of Liability - REDLINE (playbook OF-LIABILITY-CAP)

> three (3) times the fees paid or payable

OF-LIABILITY-CAP: standard cap is 12 months' fees (1x), acceptable up to 2x. A 3x general cap exceeds the auto-approve limit but does not meet the escalate_if (not uncapped, not removal beyond super-cap heads). Redline the general cap down to 2x; we can offer a 3x super-cap limited to confidentiality and data-protection breaches if the customer needs more.

**Proposed text:** two (2) times the fees paid or payable

## Estimated time

- Manual review baseline: ~25 min
- Review-only with this triage: ~18 min
- Estimated saving: ~7 min
