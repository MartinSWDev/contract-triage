"""Run the triage pipeline over every sample contract.

Usage: .venv/bin/python src/run_all.py [--only name_substring]
"""
import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline import process

ROOT = Path(__file__).parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    samples = sorted(p for p in (ROOT / "samples").iterdir()
                     if p.suffix in (".docx", ".pdf"))
    if args.only:
        samples = [p for p in samples if args.only in p.name]

    failures = []
    for sample in samples:
        try:
            process(sample, ROOT / "outputs" / sample.stem)
        except Exception as e:
            failures.append((sample.name, str(e)))
            traceback.print_exc()

    print(f"\nDone: {len(samples) - len(failures)}/{len(samples)} succeeded")
    for name, err in failures:
        print(f"  FAILED {name}: {err[:200]}")


if __name__ == "__main__":
    main()
