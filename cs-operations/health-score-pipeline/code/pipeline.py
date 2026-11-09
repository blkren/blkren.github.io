"""Weekly customer health score pipeline.

Loads a CRM export (CSV) into SQLite, scores every account with
health_score.sql, keeps a history of scores, and posts a summary of what
changed to a Slack channel.

Standard library only. Python 3.9 or later.

    python pipeline.py --self-check          # score the sample data and check it matches the Excel model
    python pipeline.py                       # score, save history, print the Slack message
    python pipeline.py --post                # ...and post it (needs SLACK_WEBHOOK_URL)
"""

import argparse
import csv
import datetime as dt
import json
import os
import sqlite3
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ACCOUNTS = HERE.parent / "data" / "accounts.csv"
DEFAULT_DB = HERE.parent / "outputs" / "health.db"
SQL_FILE = HERE / "health_score.sql"

# Column types matter: SQLite compares text and numbers differently,
# so numbers from the CSV must be stored as numbers.
ACCOUNT_COLUMNS = {
    "account_id": "TEXT PRIMARY KEY",
    "account_name": "TEXT",
    "segment": "TEXT",
    "arr_gbp": "REAL",
    "days_to_renewal": "INTEGER",
    "workflows_contracted": "INTEGER",
    "workflows_live": "INTEGER",
    "ai_features_used": "TEXT",
    "days_since_admin_login": "INTEGER",
    "customer_pulse_1to5": "INTEGER",
    "days_since_client_engaged": "INTEGER",
    "days_since_we_contacted": "INTEGER",
    "exec_sponsor": "TEXT",
    "champion": "TEXT",
    "admin_users": "INTEGER",
    "open_tickets": "INTEGER",
    "escalated_tickets": "INTEGER",
    "payment_overdue": "TEXT",
    "growth_signal": "TEXT",
}

# Published results of health_score_model.xlsx on the sample data.
EXCEL_RESULTS = {
    "accounts": 80,
    "total_arr": 1_538_250,
    "arr_at_risk": 370_750,
    "red_amber_renewing_90_days": 8,
    "capped": 10,
    "expansion_candidates": 29,
    "expansion_arr": 575_500,
    "top_5": ["Yarrow Foods", "Ember Finance", "Cobalt Charity", "Tidal Recruitment", "Maple Retail"],
}


def load_accounts(conn, csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    missing = set(ACCOUNT_COLUMNS) - set(rows[0])
    if missing:
        sys.exit(f"{csv_path} is missing columns: {', '.join(sorted(missing))}")

    columns = ", ".join(f"{name} {kind}" for name, kind in ACCOUNT_COLUMNS.items())
    conn.execute("DROP TABLE IF EXISTS accounts")
    conn.execute(f"CREATE TABLE accounts ({columns})")
    placeholders = ", ".join("?" for _ in ACCOUNT_COLUMNS)
    conn.executemany(
        f"INSERT INTO accounts VALUES ({placeholders})",
        [[row[name].strip() for name in ACCOUNT_COLUMNS] for row in rows],
    )
    return len(rows)


def save_snapshot(conn, run_date):
    """Store this run's scores. Running twice on the same date replaces that date's scores."""
    conn.execute("DELETE FROM score_history WHERE run_date = ?", (run_date,))
    conn.execute(
        """INSERT INTO score_history
           SELECT ?, account_id, account_name, arr_gbp, health_score, band, capped
           FROM scored_accounts""",
        (run_date,),
    )


def summarise(conn):
    one = lambda sql: conn.execute(sql).fetchone()[0]
    return {
        "accounts": one("SELECT COUNT(*) FROM scored_accounts"),
        "total_arr": one("SELECT SUM(arr_gbp) FROM scored_accounts"),
        "arr_at_risk": one("SELECT COALESCE(SUM(arr_gbp), 0) FROM scored_accounts WHERE band IN ('Red', 'Amber')"),
        "red_amber_renewing_90_days": one(
            "SELECT COUNT(*) FROM scored_accounts WHERE band IN ('Red', 'Amber') AND days_to_renewal <= 90"
        ),
        "capped": one("SELECT COUNT(*) FROM scored_accounts WHERE capped"),
        "expansion_candidates": one("SELECT COUNT(*) FROM scored_accounts WHERE expansion_candidate"),
        "expansion_arr": one("SELECT COALESCE(SUM(arr_gbp), 0) FROM scored_accounts WHERE expansion_candidate"),
        "top_5": [r[0] for r in conn.execute(
            "SELECT account_name FROM scored_accounts WHERE priority > 0 ORDER BY priority DESC LIMIT 5"
        )],
    }


def write_csv(conn, sql, path):
    cursor = conn.execute(sql)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([c[0] for c in cursor.description])
        writer.writerows(cursor)


def slack_message(conn, summary, run_date):
    top = conn.execute(
        """SELECT account_name, segment, arr_gbp, health_score, band, days_to_renewal, recommended_play
           FROM scored_accounts WHERE priority > 0 ORDER BY priority DESC LIMIT 5"""
    ).fetchall()
    changes = conn.execute(
        "SELECT account_name, previous_score, current_score, alert FROM score_changes ORDER BY arr_gbp DESC"
    ).fetchall()

    share = summary["arr_at_risk"] / summary["total_arr"]
    lines = [
        f"*Customer health, week of {run_date}*",
        f"£{summary['arr_at_risk']:,.0f} ARR ({share:.0%}) is red or amber. "
        f"{summary['red_amber_renewing_90_days']} of those accounts renew within 90 days.",
        "",
        "*Call first*",
    ]
    for i, (name, segment, arr, score, band, days, play) in enumerate(top, 1):
        lines.append(f"{i}. {name} ({segment}, £{arr:,.0f}): {score} {band}, renews in {days} days. {play}")

    lines += ["", "*Changed since last week*"]
    if changes:
        lines += [f"• {name}: {prev} → {cur}. {alert}" for name, prev, cur, alert in changes]
    else:
        lines.append("Nothing new. (Or this is the first run, so there is no last week to compare with.)")
    return "\n".join(lines)


def post_to_slack(text):
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url:
        sys.exit("Set SLACK_WEBHOOK_URL to a Slack incoming webhook to post, or leave out --post.")
    request = urllib.request.Request(
        url,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            sys.exit(f"Slack returned {response.status}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--accounts", type=Path, default=DEFAULT_ACCOUNTS, help="CRM export as CSV")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite file that keeps score history")
    parser.add_argument("--run-date", default=dt.date.today().isoformat(), help="defaults to today")
    parser.add_argument("--post", action="store_true", help="post the summary to Slack")
    parser.add_argument("--self-check", action="store_true", help="check results match the Excel model")
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(":memory:" if args.self_check else args.db)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS score_history (
             run_date TEXT, account_id TEXT, account_name TEXT, arr_gbp REAL,
             health_score REAL, band TEXT, capped INTEGER,
             PRIMARY KEY (run_date, account_id))"""
    )
    load_accounts(conn, args.accounts)
    conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
    summary = summarise(conn)

    if args.self_check:
        wrong = {k: (summary[k], v) for k, v in EXCEL_RESULTS.items() if summary[k] != v}
        for key, (got, expected) in wrong.items():
            print(f"MISMATCH {key}: got {got}, Excel model has {expected}")
        print("Matches the Excel model." if not wrong else f"{len(wrong)} result(s) differ.")
        sys.exit(1 if wrong else 0)

    save_snapshot(conn, args.run_date)
    conn.commit()
    out = args.db.parent
    write_csv(conn, "SELECT * FROM scored_accounts ORDER BY priority DESC, health_score", out / "scored_accounts.csv")
    write_csv(conn, "SELECT * FROM score_changes", out / "score_changes.csv")

    message = slack_message(conn, summary, args.run_date)
    print(message)
    if args.post:
        post_to_slack(message)
        print("\nPosted to Slack.")


if __name__ == "__main__":
    main()
