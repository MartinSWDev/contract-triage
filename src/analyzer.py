"""Playbook-driven analysis of an ingested contract.

Builds the prompt (playbook + template + contract), calls Claude for a
structured analysis, then deterministically verifies every quoted snippet
against the source text so no fabricated deviation survives into the
redline. Verification failures are downgraded, never silently fixed.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["doc_type", "summary", "standard_fraction", "priority",
                 "escalate_to_human", "deviations", "draft_reply"],
    "properties": {
        "doc_type": {"type": "string", "enum": ["nda", "order_form", "out_of_scope"]},
        "summary": {"type": "string",
                    "description": "2-4 sentence triage summary for the lawyer"},
        "standard_fraction": {"type": "number",
                              "description": "Fraction of the document that matches the standard template in substance, 0-1"},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "escalate_to_human": {"type": "boolean"},
        "deviations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["clause_heading", "paragraph_index", "original_snippet",
                             "rule_id", "covered", "disposition", "action",
                             "proposed_text", "comment", "reply_point"],
                "properties": {
                    "clause_heading": {"type": "string"},
                    "paragraph_index": {"type": "integer",
                                        "description": "Index of the [P#] paragraph containing the deviation"},
                    "original_snippet": {"type": "string",
                                         "description": "VERBATIM text copied from the contract that deviates. Must be an exact substring of the paragraph."},
                    "rule_id": {"type": ["string", "null"],
                                "description": "Playbook rule id, or null if no rule covers this deviation"},
                    "covered": {"type": "boolean",
                                "description": "true only if a playbook rule gives a position for this deviation"},
                    "disposition": {"type": "string",
                                    "enum": ["accept", "redline", "escalate"]},
                    "action": {"type": "string",
                               "enum": ["replace", "delete", "accept", "flag_only"],
                               "description": "replace: swap original_snippet for proposed_text; delete: strike original_snippet; accept/flag_only: comment only"},
                    "proposed_text": {"type": ["string", "null"],
                                      "description": "Replacement text for original_snippet (action=replace only)"},
                    "comment": {"type": "string",
                                "description": "Margin comment for the lawyer: what deviates, the playbook position (cite rule id), or 'NOT COVERED - needs a human'"},
                    "reply_point": {"type": ["string", "null"],
                                    "description": "Sentence for the counterparty reply, only for handled (covered) points"},
                },
            },
        },
        "draft_reply": {"type": "string",
                        "description": "Short professional email to the counterparty covering ONLY the handled points; say uncovered points are under review"},
    },
}

SYSTEM = """You are a contract triage assistant for the in-house legal team at
Fictional Co Ltd. You review incoming low-stakes commercial contracts
(mutual NDAs and customer order forms) against the team's standard templates
and playbook.

Choosing the disposition for each deviation (apply in order):
- "escalate" if EITHER the deviation is not covered by any rule (covered=false)
  OR the incoming draft meets the matching rule's DRAFT escalate_if condition
  (wording like "The draft's ... is ..."). Escalation wins even when a
  pre-approved redline exists: still fill in proposed_text as the opening
  position, but a human must own the point. Do NOT escalate on a PUSHBACK
  condition (wording like "Only if, after our redline, the counterparty
  refuses ...") - the incoming draft alone does not trigger those.
- "redline" if the deviation is outside the acceptable-without-approval range
  but the playbook fallback/redline fully resolves it and no DRAFT escalate_if
  condition is met.
- "accept" if the deviation is within the acceptable-without-approval range
  (comment only, no change).

Hard rules:
1. Only take positions that are in the playbook, and always cite the rule id.
   If a substantive deviation has no playbook rule, set rule_id to null,
   covered to false, disposition to "escalate", action to "flag_only", and
   begin the comment with "NOT COVERED - needs a human". NEVER invent legal
   advice for uncovered deviations.
2. original_snippet must be copied VERBATIM from the contract paragraph -
   exact characters, no paraphrasing, no ellipses. It is machine-checked and
   used to place tracked changes; a snippet that does not match is discarded.
3. Ignore differences that are not substantive: party names, dates, addresses,
   seat counts, fees on order forms, clause numbering, and rewording that
   preserves the same substance are NOT deviations.
4. Deletions from the standard template (e.g. a removed carve-out) ARE
   deviations: anchor them on the paragraph where the text should appear,
   quote the current (deficient) text, and propose the corrected text.
5. For proposed_text, adapt the playbook's pre-approved redline into concrete
   contract language that replaces original_snippet, keeping the surrounding
   sentence grammatical.
6. If the document is not an NDA or order form, set doc_type to "out_of_scope",
   escalate_to_human to true, list no deviations, and say in the summary that
   this document type is not handled by the playbook.
7. The draft_reply covers only handled points; for uncovered points it may say
   the team is reviewing them. Keep it short and businesslike, from
   "Fictional Legal" with no placeholders needing manual fill-in."""

PROMPT_TEMPLATE = """## Playbook (YAML)

{playbook}

## Our standard template: {template_name}

{template_text}

## Second template for classification reference: {other_name}

{other_text}

## Incoming contract ({source_note})

Paragraphs are numbered [P0], [P1], ... Use these indices in paragraph_index.

{contract_text}

Analyse the incoming contract against the matching template and the playbook.
Identify every substantive deviation (changed clauses AND added clauses AND
deleted/weakened standard protections). For each, give the playbook response
or flag it as not covered. Then produce the triage fields and the draft reply."""


def _normalise(s):
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


def _template_text(name):
    from ingest import read_docx
    paras = read_docx(ROOT / "templates" / name)
    return "\n\n".join(paras)


def build_prompt(paragraphs, source_fmt):
    playbook = (ROOT / "playbook" / "playbook.yaml").read_text()
    numbered = "\n\n".join(f"[P{i}] {p}" for i, p in enumerate(paragraphs))
    source_note = ("extracted from PDF - paragraph boundaries are approximate"
                   if source_fmt == "pdf" else "Word document")
    return PROMPT_TEMPLATE.format(
        playbook=playbook,
        template_name="Mutual NDA (MNDA-2026)",
        template_text=_template_text("nda_template.docx"),
        other_name="Order Form (under MSA-2026)",
        other_text=_template_text("order_form_template.docx"),
        source_note=source_note,
        contract_text=numbered,
    )


def verify(analysis, paragraphs):
    """Check every original_snippet is really in the contract.

    Returns the analysis with each deviation annotated:
      verified: True/False
      paragraph_index possibly corrected (searched across all paragraphs).
    Unverifiable snippets are downgraded to flag_only so the redline never
    contains a fabricated quote.
    """
    norm_paras = [_normalise(p) for p in paragraphs]
    issues = []
    for dev in analysis.get("deviations", []):
        snippet = _normalise(dev.get("original_snippet") or "")
        found_at = None
        idx = dev.get("paragraph_index")
        candidates = ([idx] if isinstance(idx, int) and 0 <= idx < len(paragraphs) else [])
        candidates += [i for i in range(len(paragraphs)) if i not in candidates]
        if snippet:
            for i in candidates:
                if snippet in norm_paras[i]:
                    found_at = i
                    break
        dev["verified"] = found_at is not None
        if found_at is not None:
            if found_at != idx:
                issues.append(f"snippet for '{dev['clause_heading']}' found in P{found_at}, model said P{idx}")
            dev["paragraph_index"] = found_at
        else:
            issues.append(f"snippet for '{dev['clause_heading']}' NOT FOUND - downgraded to flag_only")
            dev["action"] = "flag_only"
            dev["comment"] = ("[quote could not be verified against the document - "
                              "please locate manually] " + dev.get("comment", ""))
    analysis["verification_issues"] = issues
    return analysis


def derive_escalation(analysis):
    """Compute the document-level escalation flag deterministically from the
    per-deviation dispositions, so it can never contradict them. A human is
    needed if the document is out of scope, any deviation is not covered, or
    any deviation is dispositioned "escalate".
    """
    model_flag = bool(analysis.get("escalate_to_human"))
    derived = (
        analysis.get("doc_type") == "out_of_scope"
        or any(not d.get("covered", True) for d in analysis.get("deviations", []))
        or any(d.get("disposition") == "escalate" for d in analysis.get("deviations", []))
    )
    analysis["escalate_to_human"] = derived
    analysis["escalation_model_flag"] = model_flag
    return analysis


def analyse_contract(paragraphs, source_fmt):
    from llm import analyze_json
    prompt = build_prompt(paragraphs, source_fmt)
    analysis, backend = analyze_json(SYSTEM, prompt, SCHEMA)
    analysis = verify(analysis, paragraphs)
    analysis = derive_escalation(analysis)
    analysis["backend"] = backend
    return analysis
