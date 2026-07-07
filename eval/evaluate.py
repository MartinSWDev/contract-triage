"""Evaluate the assistant's outputs against ground truth.

Usage: .venv/bin/python eval/evaluate.py
Reads samples/ground_truth/*.yaml and outputs/*/*_analysis.json,
writes eval/REPORT.md and eval/results.json.

Matching rules:
- A ground-truth deviation with a rule id is CAUGHT if the assistant reported
  a deviation with the same rule id.
- A ground-truth uncovered deviation (rule: null) is CAUGHT-HONESTLY if the
  assistant reported a deviation with covered=false whose text mentions the
  topic; it is CAUGHT-BUT-HALLUCINATED if the assistant reported it but
  attached a playbook rule / invented advice (this is the trust-critical
  failure mode).
- Any reported deviation not in ground truth is a FALSE POSITIVE (benign
  paraphrases in the samples exist precisely to provoke these).
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent

# Keywords used to match ground-truth uncovered deviations (rule: null)
# to the assistant's reported deviations, since there is no rule id to match.
UNCOVERED_KEYWORDS = {
    "IP assignment of improvements/feedback": ["improvement", "feedback", "assign", "intellectual property", " ip "],
    "Most-favoured-customer / MFN pricing clause": ["favoured", "favored", "mfn", "most favoured", "most favored"],
    "Late-payment interest removed": ["interest", "late payment", "late-payment", "no interest"],
}

# Assumptions for the monthly-volume estimate (documented in the report).
MONTHLY_VOLUME = 60
LAWYER_COST_PER_HOUR = 150  # fully-loaded internal cost, GBP


def dev_text(dev):
    return " ".join(str(dev.get(k) or "") for k in
                    ("clause_heading", "original_snippet", "comment")).lower()


def evaluate_sample(gt, analysis):
    r = {"file": gt["file"], "notes": []}

    r["type_correct"] = analysis["doc_type"] == gt["doc_type"]
    if not r["type_correct"]:
        r["notes"].append(f"type: expected {gt['doc_type']}, got {analysis['doc_type']}")

    r["escalation_correct"] = bool(analysis["escalate_to_human"]) == bool(gt["escalate_to_human"])
    if not r["escalation_correct"]:
        r["notes"].append(f"escalation: expected {gt['escalate_to_human']}, got {analysis['escalate_to_human']}")

    predicted = list(analysis.get("deviations", []))
    matched_pred = set()
    caught, missed, hallucinated_advice = [], [], []

    for gt_dev in gt.get("deviations", []):
        rule = gt_dev.get("rule")
        hit = None
        if rule:
            for i, p in enumerate(predicted):
                if i not in matched_pred and p.get("rule_id") == rule:
                    hit = i
                    break
        else:
            keywords = UNCOVERED_KEYWORDS.get(gt_dev.get("topic", ""), [])
            for i, p in enumerate(predicted):
                if i in matched_pred:
                    continue
                if any(k in dev_text(p) for k in keywords):
                    hit = i
                    break
        if hit is None:
            missed.append(gt_dev)
            r["notes"].append(f"MISSED: {rule or gt_dev.get('topic')}")
        else:
            matched_pred.add(hit)
            p = predicted[hit]
            entry = {"gt": rule or gt_dev.get("topic"),
                     "predicted_rule": p.get("rule_id"),
                     "covered_pred": p.get("covered")}
            caught.append(entry)
            if rule is None and (p.get("covered") or p.get("rule_id")):
                hallucinated_advice.append(entry)
                r["notes"].append(
                    f"HALLUCINATED ADVICE on uncovered deviation "
                    f"{gt_dev.get('topic')}: assistant cited {p.get('rule_id')}")

    false_pos = [p for i, p in enumerate(predicted) if i not in matched_pred]
    for p in false_pos:
        r["notes"].append(f"FALSE POSITIVE: {p.get('clause_heading')} ({p.get('rule_id')})")

    r["caught"] = caught
    r["missed"] = [d.get("rule") or d.get("topic") for d in missed]
    r["false_positives"] = [
        {"clause": p.get("clause_heading"), "rule": p.get("rule_id"),
         "disposition": p.get("disposition")} for p in false_pos]
    r["hallucinated_advice"] = hallucinated_advice
    r["n_gt"] = len(gt.get("deviations", []))
    r["n_pred"] = len(predicted)
    r["unverified_quotes"] = sum(1 for p in predicted if not p.get("verified", True))
    r["elapsed_seconds"] = analysis.get("_meta", {}).get("elapsed_seconds")
    r["estimate"] = analysis.get("_meta", {}).get("estimate", {})
    return r


def main():
    gt_files = sorted((ROOT / "samples" / "ground_truth").glob("*.yaml"))
    results, missing = [], []
    for gt_file in gt_files:
        gt = yaml.safe_load(gt_file.read_text())
        stem = Path(gt["file"]).stem
        analysis_path = ROOT / "outputs" / stem / f"{stem}_analysis.json"
        if not analysis_path.exists():
            missing.append(gt["file"])
            continue
        analysis = json.loads(analysis_path.read_text())
        results.append(evaluate_sample(gt, analysis))

    n = len(results)
    tp = sum(len(r["caught"]) for r in results)
    fn = sum(len(r["missed"]) for r in results)
    fp = sum(len(r["false_positives"]) for r in results)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    type_acc = sum(r["type_correct"] for r in results) / n
    esc_acc = sum(r["escalation_correct"] for r in results) / n
    halluc = sum(len(r["hallucinated_advice"]) for r in results)
    unverified = sum(r["unverified_quotes"] for r in results)
    total_saved = sum(r["estimate"].get("saved", 0) for r in results)
    mean_saved = total_saved / n if n else 0
    mean_elapsed = (sum(r["elapsed_seconds"] or 0 for r in results) / n) if n else 0

    summary = {
        "samples": n,
        "type_accuracy": type_acc,
        "escalation_accuracy": esc_acc,
        "deviation_tp": tp, "deviation_fn": fn, "deviation_fp": fp,
        "precision": precision, "recall": recall,
        "hallucinated_advice_on_uncovered": halluc,
        "unverified_quotes_in_output": unverified,
        "mean_analysis_seconds": mean_elapsed,
        "mean_minutes_saved_per_contract": mean_saved,
        "missing_outputs": missing,
    }
    (ROOT / "eval" / "results.json").write_text(
        json.dumps({"summary": summary, "per_sample": results}, indent=2))

    write_report(summary, results)
    print(json.dumps(summary, indent=2))


def write_report(s, results):
    monthly_saved_h = s["mean_minutes_saved_per_contract"] * MONTHLY_VOLUME / 60
    lines = [
        "# Evaluation report",
        "",
        f"Run over {s['samples']} synthetic contracts "
        "(2 clean, 5 with playbook-covered deviations, 2 containing deviations "
        "the playbook deliberately does not cover, 1 out-of-scope document). "
        "Ground truth is defined next to the sample generator so it cannot drift "
        "from the documents. Metrics are computed by `eval/evaluate.py`; nothing "
        "below is hand-asserted.",
        "",
        "## Headline metrics",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| Document-type triage accuracy | {s['type_accuracy']:.0%} ({round(s['type_accuracy']*s['samples'])}/{s['samples']}) |",
        f"| Escalation decision accuracy | {s['escalation_accuracy']:.0%} ({round(s['escalation_accuracy']*s['samples'])}/{s['samples']}) |",
        f"| Deviation recall | {s['recall']:.0%} ({s['deviation_tp']}/{s['deviation_tp']+s['deviation_fn']}) |",
        f"| Deviation precision | {s['precision']:.0%} ({s['deviation_tp']}/{s['deviation_tp']+s['deviation_fp']}) |",
        f"| Hallucinated advice on uncovered deviations | {s['hallucinated_advice_on_uncovered']} |",
        f"| Unverified quotes that reached output | {s['unverified_quotes_in_output']} |",
        f"| Mean analysis time per contract | {s['mean_analysis_seconds']:.0f}s |",
        "",
        "## Per-sample results",
        "",
        "| Sample | Type OK | Escalation OK | Caught | Missed | False pos | Time |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['file']} | {'Y' if r['type_correct'] else 'N'} "
            f"| {'Y' if r['escalation_correct'] else 'N'} "
            f"| {len(r['caught'])}/{r['n_gt']} | {len(r['missed'])} "
            f"| {len(r['false_positives'])} | {r['elapsed_seconds']}s |")
    lines += ["", "## Failures and disagreements (kept, per the brief)", ""]
    any_notes = False
    for r in results:
        for note in r["notes"]:
            any_notes = True
            lines.append(f"- **{r['file']}**: {note}")
    if not any_notes:
        lines.append("- None recorded on this run.")
    commentary = ROOT / "eval" / "commentary.md"
    if commentary.exists():
        lines += ["", commentary.read_text().rstrip()]
    lines += [
        "",
        "## Time-saved estimate (assumptions stated, not measured)",
        "",
        "This is an *estimate*, not a measurement - no lawyer timed themselves "
        "for this prototype. Assumptions:",
        "",
        "- Manual baseline: 25 min per NDA/order form (industry surveys commonly "
        "cite 20-40 min for routine NDA review; 25 is deliberately conservative), "
        "5 min to recognise and reroute an out-of-scope document.",
        "- Assisted review: 5 min to read the triage summary and skim the "
        "redline, +2 min per flagged deviation, +5 min if escalation is needed.",
        "- The assistant's own runtime is excluded (it runs before the lawyer "
        "opens the file).",
        "",
        f"| | |",
        f"|---|---|",
        f"| Mean saving per contract | ~{s['mean_minutes_saved_per_contract']:.0f} min |",
        f"| Monthly volume assumed | {MONTHLY_VOLUME} contracts |",
        f"| Estimated monthly saving | ~{monthly_saved_h:.0f} lawyer-hours |",
        f"| At GBP {LAWYER_COST_PER_HOUR}/h fully loaded | ~GBP {monthly_saved_h*LAWYER_COST_PER_HOUR:,.0f}/month |",
        "",
        "The bigger operational win is queue latency: triage output is ready in "
        f"~{s['mean_analysis_seconds']:.0f}s, so clean contracts "
        "can turn around same-hour instead of waiting a day-plus in the queue.",
        "",
        "## Reading the numbers honestly",
        "",
        "- n=9 synthetic contracts written by the same author as the playbook. "
        "Real counterparty paper is messier: scanned PDFs, reordered clauses, "
        "definitions split across sections. Treat these numbers as an upper "
        "bound and re-run this eval on 20-30 anonymised real contracts before "
        "trusting it.",
        "- The eval matches deviations by playbook rule id, so a deviation "
        "caught under the *wrong* rule would score as a miss plus a false "
        "positive - strict by design.",
        "- 'Hallucinated advice on uncovered deviations' is the metric that "
        "matters most for trust: it counts cases where the playbook had no "
        "answer and the assistant invented one instead of escalating.",
    ]
    (ROOT / "eval" / "REPORT.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
