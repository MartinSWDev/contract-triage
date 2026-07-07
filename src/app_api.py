"""JSON API for the Tauri desktop app. Every command prints one JSON object
(or array) to stdout so the Rust side can parse it. All real work lives in the
existing pipeline; this is a thin adapter.

Usage:
    app_api.py list <dir>       -> [ {name, path, status, ...summary} ]
    app_api.py run  <path>      -> { ...summary, outputs_dir }
    app_api.py detail <path>    -> full saved analysis for one contract
    app_api.py eval             -> { ...eval summary }
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline import process, estimate_minutes  # noqa: E402

ROOT = Path(__file__).parent.parent
OUTPUTS = ROOT / "outputs"


def summarize(analysis):
    devs = analysis.get("deviations", [])
    return {
        "doc_type": analysis.get("doc_type"),
        "priority": analysis.get("priority"),
        "escalate_to_human": analysis.get("escalate_to_human"),
        "n_deviations": len(devs),
        "n_uncovered": sum(1 for d in devs if not d.get("covered", True)),
        "standard_fraction": analysis.get("standard_fraction"),
        "elapsed_seconds": analysis.get("_meta", {}).get("elapsed_seconds"),
        "minutes_saved": estimate_minutes(analysis).get("saved"),
        "unverified_quotes": sum(1 for d in devs if not d.get("verified", True)),
    }


def analysis_path(stem):
    return OUTPUTS / stem / f"{stem}_analysis.json"


def cmd_list(directory):
    d = Path(directory)
    items = []
    if d.is_dir():
        for f in sorted(d.iterdir()):
            if f.suffix.lower() not in (".docx", ".pdf"):
                continue
            ap = analysis_path(f.stem)
            entry = {"name": f.name, "path": str(f),
                     "status": "done" if ap.exists() else "pending"}
            if ap.exists():
                entry.update(summarize(json.loads(ap.read_text())))
            items.append(entry)
    return items


def cmd_run(path):
    p = Path(path)
    analysis = process(p, OUTPUTS / p.stem)
    out = summarize(analysis)
    out["name"] = p.name
    out["path"] = str(p)
    out["status"] = "done"
    out["outputs_dir"] = str(OUTPUTS / p.stem)
    return out


def cmd_detail(path):
    p = Path(path)
    ap = analysis_path(p.stem)
    if not ap.exists():
        return {"error": "not analysed yet", "name": p.name}
    a = json.loads(ap.read_text())
    return {
        "name": p.name,
        "summary": a.get("summary"),
        "draft_reply": a.get("draft_reply"),
        "escalate_to_human": a.get("escalate_to_human"),
        "outputs_dir": str(OUTPUTS / p.stem),
        "redline_file": f"{p.stem}_REDLINE.docx",
        "deviations": [
            {"clause_heading": d.get("clause_heading"),
             "rule_id": d.get("rule_id"),
             "covered": d.get("covered"),
             "disposition": d.get("disposition"),
             "verified": d.get("verified"),
             "original_snippet": d.get("original_snippet"),
             "proposed_text": d.get("proposed_text"),
             "comment": d.get("comment")}
            for d in a.get("deviations", [])
        ],
    }


def cmd_eval():
    # Re-run the evaluator, then read its machine-written summary.
    subprocess.run([sys.executable, str(ROOT / "eval" / "evaluate.py")],
                   capture_output=True, text=True, cwd=str(ROOT))
    results = json.loads((ROOT / "eval" / "results.json").read_text())
    return results["summary"]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "list":
        print(json.dumps(cmd_list(sys.argv[2])))
    elif cmd == "run":
        print(json.dumps(cmd_run(sys.argv[2])))
    elif cmd == "detail":
        print(json.dumps(cmd_detail(sys.argv[2])))
    elif cmd == "eval":
        print(json.dumps(cmd_eval()))
    else:
        print(json.dumps({"error": f"unknown command: {cmd}"}))
        sys.exit(2)


if __name__ == "__main__":
    main()
