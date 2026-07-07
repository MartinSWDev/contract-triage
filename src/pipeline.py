"""Contract triage pipeline.

Usage:
    .venv/bin/python src/pipeline.py <contract.docx|contract.pdf> [-o outputs/]

Produces, per contract:
    <name>_REDLINE.docx   - tracked changes + margin comments (the artefact)
    <name>_triage.md      - triage summary + flagged deviations
    <name>_reply_email.md - draft reply to the counterparty
    <name>_analysis.json  - raw verified analysis (used by the eval)
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ingest import load_contract
from analyzer import analyse_contract
from redline import apply_redlines, synthesize_docx_from_paragraphs

# Conservative manual-review baseline used for the time-saved estimate;
# assumptions are documented in the eval report.
MANUAL_MINUTES = {"nda": 25, "order_form": 25, "out_of_scope": 5}
REVIEW_ONLY_MINUTES_BASE = 5     # reading the triage summary + clean doc skim
REVIEW_MINUTES_PER_DEVIATION = 2  # checking each proposed redline


def triage_markdown(name, analysis, elapsed, applied, skipped):
    a = analysis
    lines = [
        f"# Triage: {name}",
        "",
        f"- **Document type:** {a['doc_type']}",
        f"- **Priority:** {a['priority']}",
        f"- **How standard:** {a['standard_fraction']:.0%} of the document matches our template",
        f"- **Needs a human:** {'YES - escalate' if a['escalate_to_human'] else 'No - all deviations covered by playbook'}",
        f"- **Deviations found:** {len(a['deviations'])} "
        f"({sum(1 for d in a['deviations'] if not d['covered'])} not covered by playbook)",
        f"- **Analysis time:** {elapsed:.0f}s (backend: {a.get('backend')})",
        "",
        "## Summary",
        "",
        a["summary"],
        "",
    ]
    if a["deviations"]:
        lines += ["## Flagged deviations", ""]
        for d in a["deviations"]:
            tag = (f"playbook {d['rule_id']}" if d.get("rule_id")
                   else "NOT COVERED - needs a human")
            check = "" if d.get("verified") else " (quote unverified - check manually)"
            lines += [
                f"### {d['clause_heading']} - {d['disposition'].upper()} ({tag}){check}",
                "",
                f"> {d['original_snippet']}",
                "",
                d["comment"],
                "",
            ]
            if d.get("proposed_text"):
                lines += [f"**Proposed text:** {d['proposed_text']}", ""]
    if analysis.get("verification_issues"):
        lines += ["## Verification notes", ""]
        lines += [f"- {i}" for i in analysis["verification_issues"]]
        lines += [""]
    handled = [h for h, act in applied]
    if skipped:
        lines += ["## Redline warnings", "",
                  f"- Could not locate paragraphs for: {', '.join(skipped)}", ""]
    est = estimate_minutes(a)
    lines += [
        "## Estimated time",
        "",
        f"- Manual review baseline: ~{est['manual']} min",
        f"- Review-only with this triage: ~{est['assisted']} min",
        f"- Estimated saving: ~{est['saved']} min",
        "",
    ]
    return "\n".join(lines)


def estimate_minutes(analysis):
    manual = MANUAL_MINUTES.get(analysis["doc_type"], 25)
    if analysis["doc_type"] == "out_of_scope":
        assisted = 2
    else:
        assisted = (REVIEW_ONLY_MINUTES_BASE
                    + REVIEW_MINUTES_PER_DEVIATION * len(analysis["deviations"]))
        if analysis["escalate_to_human"]:
            assisted += 5  # escalated points need real thought
    return {"manual": manual, "assisted": assisted,
            "saved": max(0, manual - assisted)}


def process(contract_path, out_dir):
    contract_path = Path(contract_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = contract_path.stem

    t0 = time.time()
    paragraphs, fmt = load_contract(contract_path)
    analysis = analyse_contract(paragraphs, fmt)
    elapsed = time.time() - t0

    # Redline on the original Word file; for PDFs, synthesise a Word copy.
    if fmt == "docx":
        source_docx = contract_path
    else:
        source_docx = out_dir / f"{name}_from_pdf.docx"
        synthesize_docx_from_paragraphs(paragraphs, source_docx)

    redline_path = out_dir / f"{name}_REDLINE.docx"
    applied, skipped = apply_redlines(source_docx, analysis, redline_path)

    analysis["_meta"] = {
        "file": contract_path.name,
        "elapsed_seconds": round(elapsed, 1),
        "redline_applied": [list(x) for x in applied],
        "redline_skipped": skipped,
        "estimate": estimate_minutes(analysis),
    }
    (out_dir / f"{name}_analysis.json").write_text(json.dumps(analysis, indent=2))
    (out_dir / f"{name}_triage.md").write_text(
        triage_markdown(contract_path.name, analysis, elapsed, applied, skipped))
    (out_dir / f"{name}_reply_email.md").write_text(
        f"# Draft reply - {contract_path.name}\n\n{analysis['draft_reply']}\n")

    print(f"[{name}] type={analysis['doc_type']} priority={analysis['priority']} "
          f"deviations={len(analysis['deviations'])} "
          f"escalate={analysis['escalate_to_human']} ({elapsed:.0f}s)")
    return analysis


def main():
    ap = argparse.ArgumentParser(description="Playbook-driven contract triage")
    ap.add_argument("contract", help="Path to .docx or .pdf contract")
    ap.add_argument("-o", "--out", default="outputs", help="Output directory")
    args = ap.parse_args()
    process(args.contract, Path(args.out) / Path(args.contract).stem)


if __name__ == "__main__":
    main()
