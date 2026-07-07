# Triage: nda_03_quantix_heavy_redline.docx

- **Document type:** nda
- **Priority:** high
- **How standard:** 80% of the document matches our template
- **Needs a human:** YES - escalate
- **Deviations found:** 3 (0 not covered by playbook)
- **Analysis time:** 38s (backend: cli)

## Summary

Incoming Quantix Labs MNDA tracks our MNDA-2026 template closely (term, carve-outs, governing law, mutuality all standard) but has three substantive deviations: a perpetual confidentiality period, an added residuals clause, and an added 2-year, all-employee non-solicitation clause. The confidentiality period and residuals are auto-redlined per playbook; the non-solicit meets a DRAFT escalate_if (over 12 months and beyond directly-involved employees), so a human must own that point. Route to a lawyer for the non-solicit while sending our standard redlines on the other two.

## Flagged deviations

### 6. Confidentiality Period - REDLINE (playbook NDA-CONF-PERIOD)

> The Recipient's obligations under this Agreement survive indefinitely with respect to all Confidential Information, without limitation in time.

Draft imposes a perpetual/unlimited confidentiality obligation on ordinary Confidential Information. Per NDA-CONF-PERIOD, replace with five (5) years from disclosure, retaining the trade-secret carve-out. The escalate_if here is a pushback condition, so this is auto-redlined without escalation.

**Proposed text:** The Recipient's obligations under this Agreement survive for a period of five (5) years from the date of disclosure of the relevant Confidential Information, except that obligations in respect of trade secrets continue for as long as such information remains a trade secret under applicable law.

### 9. Residuals - REDLINE (playbook NDA-RESIDUALS)

> Notwithstanding anything to the contrary herein, the Recipient may use for any purpose the Residuals resulting from access to the Confidential Information, where "Residuals" means information retained in the unaided memory of the Recipient's personnel.

Added residuals clause not in our template. Per NDA-RESIDUALS, delete in its entirety - a residuals clause effectively licenses our Confidential Information. The escalate_if is a pushback condition, so this is auto-deleted without escalation.

### 12. Non-Solicitation - ESCALATE (playbook NDA-NON-SOLICIT)

> During the term of this Agreement and for two (2) years thereafter, neither party shall directly or indirectly solicit for employment any employee of the other party.

Added non-solicit not in our NDA template. This meets the DRAFT escalate_if under NDA-NON-SOLICIT: it runs 2 years (over 12 months) AND covers any employee (beyond those directly involved in the discussions), so a human must own this point. Opening position per the pre-approved redline is to delete the clause; if pushed, limit to 12 months and employees directly involved only, with a general job-advert carve-out.

## Estimated time

- Manual review baseline: ~25 min
- Review-only with this triage: ~16 min
- Estimated saving: ~9 min
