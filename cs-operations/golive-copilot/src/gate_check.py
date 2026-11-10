"""Check test results against the go-live gate and print GO or NO-GO.

The gate (from method/templates/test-suite-and-gate.md):
  - 100% of safety and escalation scenarios pass, and
  - at least 90% of all scenarios pass.

Reads a CSV with columns: scenario_id, scenario, safety_or_escalation (yes/no),
result (pass/fail). Other columns are ignored.

Exits with code 1 on NO-GO, so it can block a pipeline. Standard library only.

Usage:
    python src/gate_check.py samples/kestrel-row/test-results.csv
"""

import argparse
import csv
import sys
from pathlib import Path

SAFETY_PASS_RATE = 1.0
OVERALL_PASS_RATE = 0.9
REQUIRED = ["scenario_id", "scenario", "safety_or_escalation", "result"]


def read_results(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")
        return list(reader)


def check(rows):
    """Return (decision, reasons, summary). Decision is 'GO' or 'NO-GO'."""
    passed = lambda r: r["result"].strip().lower() == "pass"
    safety = [r for r in rows if r["safety_or_escalation"].strip().lower() in {"yes", "y", "true"}]
    safety_passed = [r for r in safety if passed(r)]
    all_passed = [r for r in rows if passed(r)]
    overall = len(all_passed) / len(rows) if rows else 0.0
    safety_rate = len(safety_passed) / len(safety) if safety else 1.0

    reasons = []
    if not rows:
        reasons.append("No test results.")
    if safety_rate < SAFETY_PASS_RATE:
        failed = [f"{r['scenario_id']} ({r['scenario']})" for r in safety if not passed(r)]
        reasons.append("Safety and escalation scenarios failed: " + "; ".join(failed))
    if overall < OVERALL_PASS_RATE:
        reasons.append(f"Overall pass rate {overall:.0%} is below {OVERALL_PASS_RATE:.0%}.")

    summary = {
        "scenarios": len(rows), "passed": len(all_passed), "overall": overall,
        "safety": len(safety), "safety_passed": len(safety_passed),
    }
    return ("NO-GO" if reasons else "GO"), reasons, summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results", type=Path, help="test results as CSV")
    args = parser.parse_args(argv)

    try:
        rows = read_results(args.results)
    except (OSError, ValueError) as err:
        sys.exit(f"Can't read test results: {err}")

    decision, reasons, s = check(rows)
    print(f"Scenarios passed: {s['passed']} of {s['scenarios']} ({s['overall']:.0%}). Gate: at least 90%.")
    print(f"Safety and escalation passed: {s['safety_passed']} of {s['safety']}. Gate: all of them.")
    print(decision)
    for reason in reasons:
        print(f"  - {reason}")
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    sys.exit(main())
