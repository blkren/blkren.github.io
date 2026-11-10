"""Count the parts of a log review that don't need judgement, and write them as a markdown report.

Reads a conversation log (CSV), checks its columns against the expected schema,
and works out: conversations, out-of-hours share, outcomes by type, abandoned
conversations, escalations picked up later than a threshold, staff overrides by
site, the value ledger, and the health score inputs that can be counted from a log.

Anything that needs judgement (wrong information, missed escalations, unsafe
handling, compliance risk) is left to the log-review skill. Pass the conversations
the skill flagged for Quality or Outcomes with --flagged to get the final
resolution rate and correct handling rate.

THE LOG SCHEMA IS AN ASSUMPTION. It matches the fictional sample, not any real
product's export. Replace EXPECTED_COLUMNS with the real schema before using it.

Standard library only. No network calls.

Usage:
    python src/log_metrics.py samples/kestrel-row/logs.csv
    python src/log_metrics.py samples/kestrel-row/logs.csv --threshold 15
    python src/log_metrics.py samples/kestrel-row/logs.csv --flagged KR-002,KR-006,KR-007,KR-008,KR-009,KR-012
"""

import argparse
import csv
import datetime as dt
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORTS = HERE.parent / "reports"

# Assumed schema. Some exports call the site column "branch", so that is accepted too.
EXPECTED_COLUMNS = [
    "conversation_id", "site", "channel", "timestamp", "out_of_hours", "intent",
    "transcript", "outcome", "escalation_ack_minutes", "staff_override",
]
OPTIONAL_COLUMNS = ["customer_ref"]
COLUMN_ALIASES = {"branch": "site"}

# Outcomes that count as "reached an outcome" (resolved, booked or job raised).
OUTCOME_REACHED = {"resolved", "viewing_booked", "valuation_booked", "appointment_booked", "booked", "job_raised"}

JUDGEMENT = "Run the log-review skill for this section."


def is_true(value):
    return str(value).strip().lower() in {"true", "yes", "y", "1"}


def pct(part, whole):
    return f"{part / whole:.0%}" if whole else "n/a"


def read_log(path):
    """Read the CSV and return (rows, schema notes). Renames aliased columns."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        found = list(reader.fieldnames or [])
        rows = [{COLUMN_ALIASES.get(k, k): v for k, v in row.items()} for row in reader]
    renamed = [f"`{c}` read as `{COLUMN_ALIASES[c]}`" for c in found if c in COLUMN_ALIASES]
    found = [COLUMN_ALIASES.get(c, c) for c in found]
    schema = {
        "missing": [c for c in EXPECTED_COLUMNS if c not in found],
        "extra": [c for c in found if c not in EXPECTED_COLUMNS + OPTIONAL_COLUMNS],
        "optional_missing": [c for c in OPTIONAL_COLUMNS if c not in found],
        "renamed": renamed,
    }
    return rows, schema


def repeat_contacts(rows, hours=72):
    """IDs of conversations followed by another from the same customer within `hours`."""
    by_customer = {}
    for row in rows:
        ref = (row.get("customer_ref") or "").strip()
        if ref:
            when = dt.datetime.fromisoformat(row["timestamp"])
            by_customer.setdefault(ref, []).append((when, row["conversation_id"]))
    repeats = set()
    for contacts in by_customer.values():
        contacts.sort()
        for (first, cid), (second, _) in zip(contacts, contacts[1:]):
            if second - first <= dt.timedelta(hours=hours):
                repeats.add(cid)
    return repeats


def calculate(rows, threshold=30, flagged=None):
    """Return a dictionary of every metric. `flagged` is a set of conversation IDs, or None."""
    get = lambda row, col: (row.get(col) or "").strip()
    total = len(rows)
    ooh = [r for r in rows if is_true(get(r, "out_of_hours"))]
    outcomes = Counter(get(r, "outcome") or "(blank)" for r in rows)
    escalations = [r for r in rows if get(r, "escalation_ack_minutes")]
    late = [r for r in escalations if float(get(r, "escalation_ack_minutes")) > threshold]
    overrides = [r for r in rows if is_true(get(r, "staff_override"))]
    reached = [r for r in rows if get(r, "outcome") in OUTCOME_REACHED]

    m = {
        "conversations": total,
        "out_of_hours": len(ooh),
        "outcomes": dict(outcomes),
        "outcome_reached": len(reached),
        "abandoned": outcomes.get("abandoned", 0),
        "escalations": len(escalations),
        "late_escalations": [get(r, "conversation_id") for r in late],
        "threshold": threshold,
        "overrides_by_site": dict(Counter(get(r, "site") or "(blank)" for r in overrides)),
        "overrides": [get(r, "conversation_id") for r in overrides],
        "sites": sorted({get(r, "site") or "(blank)" for r in rows}),
        "repeat_check": any(get(r, "customer_ref") for r in rows),
        "flagged": flagged,
    }

    # Value ledger: each outcome type, out of hours versus in hours.
    ledger = {}
    for r in rows:
        key = get(r, "outcome") or "(blank)"
        side = "ooh" if is_true(get(r, "out_of_hours")) else "in_hours"
        ledger.setdefault(key, {"ooh": [], "in_hours": []})[side].append(get(r, "conversation_id"))
    m["ledger"] = ledger

    # The two rates need the log-review skill's Quality and Outcomes flags.
    if flagged is not None:
        repeats = repeat_contacts(rows)
        resolutions = [r for r in reached
                       if not is_true(get(r, "staff_override"))
                       and get(r, "conversation_id") not in flagged
                       and get(r, "conversation_id") not in repeats]
        correct_escalations = [r for r in rows
                               if get(r, "outcome") == "escalated" and get(r, "conversation_id") not in flagged]
        redone_but_right = [r for r in overrides if get(r, "conversation_id") not in flagged]
        m["resolutions"] = [get(r, "conversation_id") for r in resolutions]
        m["correct_escalations"] = [get(r, "conversation_id") for r in correct_escalations]
        m["redone_but_right"] = [get(r, "conversation_id") for r in redone_but_right]
        m["correctly_handled"] = len(resolutions) + len(correct_escalations) + len(redone_but_right)
    return m


def ids(items):
    return ", ".join(items) if items else "none"


def render(m, source, schema):
    """Build the markdown report. Headings follow the log-review skill's summary steps."""
    total = m["conversations"]
    on_time = m["escalations"] - len(m["late_escalations"])
    lines = [
        f"# Log metrics: {source}",
        "",
        f"Generated by `src/log_metrics.py` on {dt.date.today().isoformat()}. This report holds the counts only. "
        "Sections marked for the log-review skill need judgement.",
        "",
        "> The log schema is an assumption for this kit. Replace it with the real export before relying on these figures.",
        "",
        "## Schema check",
        "",
        f"- Missing expected columns: {ids(schema['missing'])}",
        f"- Extra columns (ignored): {ids(schema['extra'])}",
        f"- Optional columns not present: {ids(schema['optional_missing'])}",
    ]
    if schema["renamed"]:
        lines.append(f"- Renamed: {', '.join(schema['renamed'])}")
    lines += [
        "",
        "## 1. Headline",
        "",
        f"- Conversations reviewed: {total}",
        f"- Out of hours: {m['out_of_hours']} ({pct(m['out_of_hours'], total)})",
        f"- Reached an outcome (resolved, booked or job raised): {m['outcome_reached']}. This is not the resolution rate.",
        f"- Escalated: {m['outcomes'].get('escalated', 0)}. Abandoned: {m['abandoned']}.",
        f"- Escalations picked up later than {m['threshold']} minutes: {len(m['late_escalations'])} ({ids(m['late_escalations'])})",
        f"- Staff overrides: {len(m['overrides'])} ({ids(m['overrides'])})",
        f"- Critical flags: {JUDGEMENT}",
        "",
        "**Outcomes by type**",
        "",
        "| Outcome | Conversations |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in sorted(m["outcomes"].items())]
    lines += [
        "",
        "**Staff overrides by site**",
        "",
        "| Site | Overrides |",
        "|---|---|",
    ]
    lines += [f"| {s} | {m['overrides_by_site'].get(s, 0)} |" for s in m["sites"]]
    lines += [
        "",
        "**Flags that need judgement:** wrong information, missed escalations, unsafe handling, compliance risk. "
        + JUDGEMENT,
        "",
        "## Health score inputs",
        "",
        "| Input | Value | Note |",
        "|---|---|---|",
        "| A1 Coverage of eligible work | Not measurable | Needs channel logs, not just conversations the AI agent saw |",
        f"| A2 Bypass rate (signal) | {len(m['overrides'])} of {total} ({pct(len(m['overrides']), total)}) | Staff overrides. The log-review skill confirms which were bypass |",
        f"| Q3 Escalations picked up within {m['threshold']} minutes | {on_time} of {m['escalations']} ({pct(on_time, m['escalations'])}) | |",
    ]
    if m["flagged"] is None:
        lines.append(f"| V2 Resolution rate | Needs judgement | Rerun with `--flagged` and the Quality and Outcomes flags from the log-review skill |")
    else:
        res = len(m["resolutions"])
        lines.append(f"| V2 Resolution rate | {res} of {total} ({pct(res, total)}) | {ids(m['resolutions'])} |")
        lines.append(
            f"| Correct handling rate (diagnostic) | {m['correctly_handled']} of {total} ({pct(m['correctly_handled'], total)}) | "
            f"Resolutions, plus correct escalations ({ids(m['correct_escalations'])}), "
            f"plus outcomes staff redid where the AI was right ({ids(m['redone_but_right'])}) |")
    if not m["repeat_check"]:
        lines += ["", "*Repeat contact within 72 hours couldn't be checked: the log has no `customer_ref` column.*"]
    lines += ["", "## 2. By bucket", "", JUDGEMENT, "", "## 3. Clusters", "", JUDGEMENT, "",
              "## 4. Outcomes for the value ledger", "",
              "| Outcome | Out of hours | In hours |", "|---|---|---|"]
    for outcome, sides in sorted(m["ledger"].items()):
        cell = lambda xs: f"{len(xs)} ({ids(xs)})" if xs else "0"
        lines.append(f"| {outcome} | {cell(sides['ooh'])} | {cell(sides['in_hours'])} |")
    for heading in ["5. Actions", "6. Bug reports", "7. Product feedback", "8. Template candidates", "9. Gate check"]:
        lines += ["", f"## {heading}", "", JUDGEMENT]
    return "\n".join(lines) + "\n"


def report_name(path):
    """samples/kestrel-row/logs.csv -> log-metrics-kestrel-row.md"""
    stem = path.parent.name if path.stem == "logs" else path.stem
    return f"log-metrics-{stem}.md"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("log", type=Path, help="conversation log as CSV")
    parser.add_argument("--threshold", type=float, default=30, help="minutes before an escalation counts as late (default 30)")
    parser.add_argument("--flagged", help="comma-separated IDs the log-review skill flagged for Quality or Outcomes")
    parser.add_argument("--out", type=Path, help="report path (default reports/log-metrics-<name>.md)")
    args = parser.parse_args(argv)

    if not args.log.exists():
        sys.exit(f"Log file not found: {args.log}")
    rows, schema = read_log(args.log)
    if "conversation_id" in schema["missing"]:
        sys.exit("The log has no conversation_id column, so nothing can be counted.")
    for col in schema["missing"]:
        print(f"Warning: column '{col}' is missing; figures that use it will be blank or zero.")
    for row in rows:  # keep going on missing columns by treating them as blank
        for col in schema["missing"]:
            row.setdefault(col, "")

    flagged = None if args.flagged is None else {x.strip() for x in args.flagged.split(",") if x.strip()}
    threshold = int(args.threshold) if args.threshold == int(args.threshold) else args.threshold
    metrics = calculate(rows, threshold=threshold, flagged=flagged)

    out = args.out or REPORTS / report_name(args.log)
    out.parent.mkdir(parents=True, exist_ok=True)
    source = args.log.parent.name if args.log.stem == "logs" else args.log.stem
    out.write_text(render(metrics, source, schema), encoding="utf-8")

    print(f"{metrics['conversations']} conversations, {metrics['out_of_hours']} out of hours, "
          f"{metrics['abandoned']} abandoned, {len(metrics['late_escalations'])} escalation(s) over "
          f"{threshold} minutes, {len(metrics['overrides'])} staff overrides.")
    print(f"Report written to {out}")
    return metrics


if __name__ == "__main__":
    main()
