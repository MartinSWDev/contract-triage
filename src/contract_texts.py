"""Template clause texts and synthetic sample definitions.

Each template is an ordered list of (heading, text) clauses. Samples are
defined as modifications of a template: replaced clauses, inserted clauses,
and deleted clauses. Ground truth for the eval is defined alongside each
sample so it can never drift from the documents themselves.
"""

NDA_TITLE = "MUTUAL NON-DISCLOSURE AGREEMENT"
NDA_INTRO = (
    'This Mutual Non-Disclosure Agreement (this "Agreement") is entered into as of '
    '{date} (the "Effective Date") between Fictional Co Ltd, a company '
    "registered in England and Wales with company number 09876543, whose registered "
    'office is at Example House, 1 Sample Street, London EC1A 1AA ("Fictional Co"), and {party}, '
    '("Counterparty"). Each party may disclose ("Discloser") or receive '
    '("Recipient") Confidential Information under this Agreement.'
)

NDA_CLAUSES = [
    ("Purpose",
     "The parties wish to explore a potential business relationship concerning data "
     "analytics services (the \"Purpose\") and, in connection with the Purpose, each "
     "party may disclose Confidential Information to the other."),
    ("Confidential Information",
     "\"Confidential Information\" means any non-public information disclosed by a "
     "Discloser to a Recipient, whether orally, in writing or in any other form, that "
     "is designated as confidential or that a reasonable person would understand to be "
     "confidential given the nature of the information and the circumstances of "
     "disclosure, including business plans, customer lists, financial information, "
     "product roadmaps, source code and technical data."),
    ("Exclusions",
     "Confidential Information does not include information that: (a) is or becomes "
     "publicly available other than through breach of this Agreement; (b) was known to "
     "the Recipient without restriction before disclosure; (c) is independently "
     "developed by the Recipient without use of the Discloser's Confidential "
     "Information; (d) is rightfully received from a third party without a duty of "
     "confidentiality; or (e) is required to be disclosed by law or court order, "
     "provided the Recipient gives the Discloser prompt written notice where lawful "
     "and reasonable assistance to contest or limit the disclosure."),
    ("Obligations",
     "The Recipient shall: (a) use Confidential Information solely for the Purpose; "
     "(b) protect it using at least the degree of care it uses for its own confidential "
     "information, and no less than reasonable care; (c) not disclose it to any third "
     "party except to its employees, officers and professional advisers who need to "
     "know it for the Purpose and are bound by confidentiality obligations no less "
     "protective than this Agreement; and (d) notify the Discloser promptly upon "
     "becoming aware of any unauthorised use or disclosure."),
    ("Term",
     "This Agreement commences on the Effective Date and continues for a period of "
     "two (2) years, unless terminated earlier by either party on thirty (30) days' "
     "written notice."),
    ("Confidentiality Period",
     "The Recipient's obligations under this Agreement survive for three (3) years "
     "from the date of disclosure of the relevant Confidential Information, except "
     "that obligations in respect of trade secrets continue for as long as such "
     "information remains a trade secret under applicable law."),
    ("Return or Destruction",
     "Upon the Discloser's written request or upon expiry or termination of this "
     "Agreement, the Recipient shall promptly return or destroy all Confidential "
     "Information in its possession, save that the Recipient may retain copies "
     "required by law or by bona fide document-retention policies, which remain "
     "subject to this Agreement."),
    ("No Licence",
     "Nothing in this Agreement grants either party any licence or other right in or "
     "to the other party's Confidential Information or intellectual property, except "
     "the limited right to use Confidential Information for the Purpose."),
    ("No Warranty",
     "All Confidential Information is provided \"as is\". Neither party warrants the "
     "accuracy or completeness of any Confidential Information disclosed under this "
     "Agreement."),
    ("Remedies",
     "Each party acknowledges that unauthorised use or disclosure of Confidential "
     "Information may cause irreparable harm for which damages may be an inadequate "
     "remedy, and that the Discloser is entitled to seek injunctive or other "
     "equitable relief in addition to any other remedies available at law."),
    ("Governing Law",
     "This Agreement is governed by the laws of England and Wales, and the courts of "
     "England shall have exclusive jurisdiction over any dispute arising out of or in "
     "connection with it."),
    ("General",
     "Neither party may assign this Agreement without the other party's prior written "
     "consent. This Agreement constitutes the entire agreement between the parties "
     "concerning its subject matter and may be executed in counterparts. No failure "
     "or delay in exercising any right constitutes a waiver of it."),
]

OF_TITLE = "ORDER FORM"
OF_INTRO = (
    "This Order Form is entered into as of {date} between Fictional Co Ltd "
    '("Provider") and {party} ("Customer") and is governed by the Master '
    "Subscription Agreement between the parties dated {msa_date} (the \"MSA\"). "
    "Capitalised terms not defined in this Order Form have the meanings given in the MSA."
)

OF_CLAUSES = [
    ("Services and Subscription",
     "Provider will make the Fictional Analytics Platform (Professional tier) available "
     "to Customer for up to {seats} named users, together with standard support, for "
     "the Subscription Term set out below."),
    ("Fees",
     "Customer shall pay subscription fees of {fees} per annum, exclusive of VAT. "
     "Fees are fixed for the Initial Term except as set out in clause 5 (Renewal "
     "Price Increases)."),
    ("Payment Terms",
     "Provider will invoice annually in advance. Invoices are payable within thirty "
     "(30) days of the invoice date. Late amounts accrue interest at 4% above the "
     "Bank of England base rate."),
    ("Term and Renewal",
     "The Initial Term is twelve (12) months from the Subscription Start Date. This "
     "Order Form automatically renews for successive twelve (12) month periods unless "
     "either party gives written notice of non-renewal at least sixty (60) days "
     "before the end of the then-current term."),
    ("Renewal Price Increases",
     "Provider may increase the subscription fees at each renewal by no more than "
     "the greater of seven percent (7%) or the percentage increase in the Consumer "
     "Prices Index over the preceding twelve months."),
    ("Limitation of Liability",
     "Subject to the exclusions in the MSA, each party's total aggregate liability "
     "arising out of or in connection with this Order Form is limited to the fees "
     "paid or payable by Customer under this Order Form in the twelve (12) months "
     "preceding the event giving rise to the claim."),
    ("Termination",
     "Either party may terminate this Order Form for the other party's material "
     "breach that remains uncured thirty (30) days after written notice. This Order "
     "Form does not include a right to terminate for convenience."),
    ("Governing Law",
     "This Order Form is governed by the laws of England and Wales, and the courts "
     "of England shall have exclusive jurisdiction over any dispute arising out of "
     "or in connection with it."),
    ("General",
     "In the event of conflict between this Order Form and the MSA, this Order Form "
     "prevails. This Order Form may be executed in counterparts."),
]

# ---------------------------------------------------------------------------
# Sample definitions.
# Each sample: base template, party, format, list of edits, and ground truth.
# Edit kinds: replace (clause heading -> new text), insert (position, heading,
# text). Paraphrases are edits that are NOT deviations (they test false
# positives) and are recorded in ground truth as benign.
# ---------------------------------------------------------------------------

SAMPLES = [
    {
        "name": "nda_01_borealis_clean",
        "base": "nda",
        "format": "docx",
        "party": "Borealis Software GmbH, Friedrichstrasse 68, 10117 Berlin, Germany",
        "date": "1 July 2026",
        "replace": {},
        "insert": [],
        "ground_truth": {
            "doc_type": "nda",
            "escalate_to_human": False,
            "deviations": [],
            "benign_edits": [],
        },
    },
    {
        "name": "nda_02_helios_term_govlaw",
        "base": "nda",
        "format": "docx",
        "party": "Helios Energy Corp., 200 Park Avenue, New York, NY 10166, USA",
        "date": "3 July 2026",
        "replace": {
            "Term": (
                "This Agreement commences on the Effective Date and continues for a "
                "period of five (5) years, unless terminated earlier by either party "
                "on thirty (30) days' written notice."),
            "Governing Law": (
                "This Agreement is governed by the laws of the State of New York, and "
                "the state and federal courts located in New York County shall have "
                "exclusive jurisdiction over any dispute arising out of or in "
                "connection with it."),
        },
        "insert": [],
        "ground_truth": {
            "doc_type": "nda",
            "escalate_to_human": False,
            "deviations": [
                {"rule": "NDA-TERM", "covered": True,
                 "note": "5-year term; within fallback (accept up to 5 years)."},
                {"rule": "NDA-GOV-LAW", "covered": True,
                 "note": "New York law; in the acceptable list (accept as-is)."},
            ],
            "benign_edits": [],
        },
    },
    {
        "name": "nda_03_quantix_heavy_redline",
        "base": "nda",
        "format": "docx",
        "party": "Quantix Labs Inc., 500 Howard Street, San Francisco, CA 94105, USA",
        "date": "6 July 2026",
        "replace": {
            "Confidentiality Period": (
                "The Recipient's obligations under this Agreement survive "
                "indefinitely with respect to all Confidential Information, without "
                "limitation in time."),
            # Paraphrase of Purpose - benign, must NOT be flagged.
            "Purpose": (
                "The parties intend to evaluate a potential commercial collaboration "
                "relating to data analytics services (the \"Purpose\"), and in "
                "connection therewith each party may make Confidential Information "
                "available to the other."),
        },
        "insert": [
            {"after": "Remedies", "heading": "Non-Solicitation",
             "text": (
                 "During the term of this Agreement and for two (2) years thereafter, "
                 "neither party shall directly or indirectly solicit for employment "
                 "any employee of the other party.")},
            {"after": "No Licence", "heading": "Residuals",
             "text": (
                 "Notwithstanding anything to the contrary herein, the Recipient may "
                 "use for any purpose the Residuals resulting from access to the "
                 "Confidential Information, where \"Residuals\" means information "
                 "retained in the unaided memory of the Recipient's personnel.")},
        ],
        "ground_truth": {
            "doc_type": "nda",
            "escalate_to_human": True,  # non-solicit exceeds 12m fallback -> escalate_if
            "deviations": [
                {"rule": "NDA-CONF-PERIOD", "covered": True,
                 "note": "Perpetual confidentiality; playbook redline to 5 years."},
                {"rule": "NDA-NON-SOLICIT", "covered": True,
                 "note": "2-year mutual non-solicit added; exceeds 12-month fallback -> delete/narrow, escalate if pushed."},
                {"rule": "NDA-RESIDUALS", "covered": True,
                 "note": "Residuals clause added; playbook says delete."},
            ],
            "benign_edits": ["Purpose paraphrased - same substance"],
        },
    },
    {
        "name": "nda_04_vantage_ip_grab",
        "base": "nda",
        "format": "docx",
        "party": "Vantage Robotics Pty Ltd, 12 Collins Street, Melbourne VIC 3000, Australia",
        "date": "6 July 2026",
        "replace": {
            "Term": (
                "This Agreement commences on the Effective Date and continues for a "
                "period of three (3) years, unless terminated earlier by either party "
                "on thirty (30) days' written notice."),
        },
        "insert": [
            {"after": "No Licence", "heading": "Improvements and Feedback",
             "text": (
                 "Any improvements, derivative works, inventions or feedback "
                 "conceived by either party in connection with the Purpose, whether "
                 "or not incorporating Confidential Information, shall be the sole "
                 "and exclusive property of Vantage Robotics Pty Ltd, and Fictional Co "
                 "hereby assigns all right, title and interest in the same to "
                 "Vantage Robotics Pty Ltd.")},
        ],
        "ground_truth": {
            "doc_type": "nda",
            "escalate_to_human": True,
            "deviations": [
                {"rule": "NDA-TERM", "covered": True,
                 "note": "3-year term; within acceptable range (accept, no redline needed)."},
                {"rule": None, "covered": False,
                 "topic": "IP assignment of improvements/feedback",
                 "note": "Broad IP assignment smuggled into NDA - no playbook rule; must be flagged NOT COVERED."},
            ],
            "benign_edits": [],
        },
    },
    {
        "name": "nda_05_osaka_pdf",
        "base": "nda",
        "format": "pdf",
        "party": "Osaka Digital KK, 2-4-9 Umeda, Kita-ku, Osaka 530-0001, Japan",
        "date": "2 July 2026",
        "replace": {
            "Exclusions": (
                "Confidential Information does not include information that: (a) is "
                "or becomes publicly available other than through breach of this "
                "Agreement; (b) was known to the Recipient without restriction before "
                "disclosure; or (c) is rightfully received from a third party without "
                "a duty of confidentiality."),
            "Governing Law": (
                "This Agreement is governed by the laws of Japan, and the Osaka "
                "District Court shall have exclusive jurisdiction over any dispute "
                "arising out of or in connection with it."),
        },
        "insert": [],
        "ground_truth": {
            "doc_type": "nda",
            "escalate_to_human": True,  # Japan not in acceptable jurisdictions
            "deviations": [
                {"rule": "NDA-CARVEOUTS", "covered": True,
                 "note": "Independent-development and legal-disclosure carve-outs deleted; reinstate per playbook."},
                {"rule": "NDA-GOV-LAW", "covered": True,
                 "note": "Japan not in acceptable list; playbook redline reverts to England & Wales; escalate if refused."},
            ],
            "benign_edits": [],
        },
    },
    {
        "name": "of_01_atlas_clean",
        "base": "order_form",
        "format": "docx",
        "party": "Atlas Freight Ltd, 1 Canada Square, London E14 5AB, United Kingdom",
        "date": "30 June 2026",
        "seats": "50", "fees": "GBP 48,000", "msa_date": "12 May 2026",
        "replace": {},
        "insert": [],
        "ground_truth": {
            "doc_type": "order_form",
            "escalate_to_human": False,
            "deviations": [],
            "benign_edits": [],
        },
    },
    {
        "name": "of_02_northwind_payment_liability",
        "base": "order_form",
        "format": "docx",
        "party": "Northwind Retail Group plc, 55 Deansgate, Manchester M3 2AY, United Kingdom",
        "date": "4 July 2026",
        "seats": "200", "fees": "GBP 180,000", "msa_date": "20 June 2026",
        "replace": {
            "Payment Terms": (
                "Provider will invoice annually in advance. Invoices are payable "
                "within ninety (90) days of the invoice date. No interest shall "
                "accrue on late amounts."),
            "Limitation of Liability": (
                "Subject to the exclusions in the MSA, each party's total aggregate "
                "liability arising out of or in connection with this Order Form is "
                "limited to three (3) times the fees paid or payable by Customer "
                "under this Order Form in the twelve (12) months preceding the event "
                "giving rise to the claim."),
            "Term and Renewal": (
                "The Initial Term is twelve (12) months from the Subscription Start "
                "Date. This Order Form does not renew automatically; any renewal "
                "shall be by written agreement of the parties."),
        },
        "insert": [],
        "ground_truth": {
            # Corrected after the first eval run (see eval/commentary.md):
            # Net 90 is beyond the Net-60 fallback ceiling, so OF-PAYMENT's
            # DRAFT escalate_if fires -> escalate. The deleted late-payment
            # interest sentence is a genuine uncovered deviation the first
            # ground truth missed; the assistant caught it.
            "doc_type": "order_form",
            "escalate_to_human": True,
            "deviations": [
                {"rule": "OF-PAYMENT", "covered": True,
                 "note": "Net 90 requested; beyond Net-60 ceiling -> redline to Net 60 AND escalate."},
                {"rule": None, "covered": False,
                 "topic": "Late-payment interest removed",
                 "note": "Deletion of the late-payment interest sentence; no playbook rule -> NOT COVERED."},
                {"rule": "OF-LIABILITY-CAP", "covered": True,
                 "note": "3x general cap; playbook redline to 2x general + 3x super-cap for confidentiality/data protection."},
                {"rule": "OF-AUTORENEW", "covered": True,
                 "note": "Auto-renewal removed; acceptable without approval (accept)."},
            ],
            "benign_edits": [],
        },
    },
    {
        "name": "of_03_zephyr_uncapped_mfn",
        "base": "order_form",
        "format": "pdf",
        "party": "Zephyr Airlines SA, 8 Place Vendome, 75001 Paris, France",
        "date": "6 July 2026",
        "seats": "500", "fees": "EUR 420,000", "msa_date": "15 June 2026",
        "replace": {
            "Limitation of Liability": (
                "Notwithstanding anything in the MSA, Provider's liability arising "
                "out of or in connection with this Order Form shall be unlimited. "
                "Customer's total aggregate liability is limited to the fees paid in "
                "the twelve (12) months preceding the event giving rise to the claim."),
        },
        "insert": [
            {"after": "Fees", "heading": "Most Favoured Customer",
             "text": (
                 "Provider represents and warrants that the fees and terms offered "
                 "to Customer are no less favourable than those offered to any other "
                 "customer of Provider, and shall extend to Customer and its "
                 "affiliates any more favourable fees or terms offered to any other "
                 "customer during the Subscription Term.")},
        ],
        "ground_truth": {
            "doc_type": "order_form",
            "escalate_to_human": True,
            "deviations": [
                {"rule": "OF-LIABILITY-CAP", "covered": True,
                 "note": "Uncapped one-sided liability - matches OF-LIABILITY-CAP escalate_if; propose 2x cap, escalate."},
                {"rule": None, "covered": False,
                 "topic": "Most-favoured-customer / MFN pricing clause",
                 "note": "MFN clause added - no playbook rule; must be flagged NOT COVERED."},
            ],
            "benign_edits": [],
        },
    },
    {
        "name": "misc_09_offer_letter",
        "base": "offer_letter",
        "format": "docx",
        "party": "Jordan Reyes",
        "date": "7 July 2026",
        "replace": {},
        "insert": [],
        "ground_truth": {
            "doc_type": "out_of_scope",
            "escalate_to_human": True,
            "deviations": [],
            "benign_edits": [],
        },
    },
]

OFFER_LETTER_TITLE = "OFFER OF EMPLOYMENT"
OFFER_LETTER_BODY = [
    ("Position",
     "Fictional Co Ltd is pleased to offer Jordan Reyes the position of Senior "
     "Data Engineer, reporting to the Head of Engineering, commencing on 1 September 2026."),
    ("Compensation",
     "Your annual base salary will be GBP 92,000, paid monthly in arrears, together "
     "with participation in the company bonus scheme at a target of 10% of base salary."),
    ("Benefits",
     "You will be eligible for 25 days' holiday per year plus bank holidays, private "
     "medical insurance, and the company pension scheme with a 5% employer contribution."),
    ("Conditions",
     "This offer is conditional on satisfactory references, proof of your right to "
     "work in the United Kingdom, and your acceptance within 14 days of the date of "
     "this letter."),
]
