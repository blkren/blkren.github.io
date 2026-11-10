"""Pre-call account brief, drafted by Claude from health score data.

Reads one account from the AI agent health score data, asks Claude for a
two-minute brief, then checks the brief before saving it: every number must
come from the data, and every risk must cite real fields. If the check fails,
nothing is saved.

    pip install -r requirements.txt
    python brief.py "Fenwick Gas Services" --dry-run   # show the facts and prompt, no API call
    python brief.py "Fenwick Gas Services"             # needs ANTHROPIC_API_KEY
    python brief.py --all
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUTPUTS = HERE.parent / "outputs"

# The play for each weakest dimension, as set out in the AI agent health score.
PLAYS = {
    "Value realised": "Run a value review: re-baseline the outcome KPI, share an ROI summary, agree the next target.",
    "Adoption and embedding": "Adoption sprint: coverage audit, close channel gaps, retrain staff, tackle bypass with the team lead.",
    "AI quality and trust": "Quality escalation: error review with Product, fix the top three error patterns, confirm the hand-off time.",
    "Flow and service delivery": "Unblock delivery: triage ageing issues with Engineering, set a fix date, review the change process.",
    "Relationship and sentiment": "Re-engage: executive sponsor meeting, identify or develop a new champion, close the loop on feedback.",
    "Commercial": "Commercial review: right-size the contract, resolve billing, review cost to serve.",
}

SYSTEM_PROMPT = """You prepare a Customer Success Manager for a call with one customer of an AI agent product. \
The agent answers calls and messages, books appointments and triages urgent requests for regulated service \
businesses. You get that account's health score data as JSON. Write a brief the CSM can read in two minutes \
before the call.

Rules:
- Use only the facts given. Every number you write must appear in the facts. You may show a rate between 0 and 1 \
as a percentage, and write money in full, for example £60,000.
- For each risk, put the exact names of the facts that support it in `evidence`.
- If a red flag is set, lead with it.
- Don't give clinical, legal or regulatory advice. Where one of those questions comes up, say who should answer it.
- Plain UK English, short sentences, no filler."""

BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string", "description": "One sentence: the single thing the CSM must know."},
        "situation": {"type": "string", "description": "Two or three sentences on where the account stands."},
        "risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "point": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["point", "evidence"],
                "additionalProperties": False,
            },
        },
        "questions": {"type": "array", "items": {"type": "string"}, "description": "Three questions to ask on the call."},
        "next_step": {"type": "string"},
    },
    "required": ["headline", "situation", "risks", "questions", "next_step"],
    "additionalProperties": False,
}


def read_csv(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return {row["Account"]: row for row in csv.DictReader(f)}


def load_facts(account):
    """Facts for one account, plus the metrics with no data. Gaps are worked out here, not by the model."""
    metrics, scores = read_csv("accounts.csv"), read_csv("scores.csv")
    if account not in metrics or account not in scores:
        sys.exit(f"No account called {account!r}. Choose from: {', '.join(metrics)}")

    facts, gaps = {}, []
    for field, value in {**metrics[account], **scores[account]}.items():
        value = value.strip()
        if value == "":
            gaps.append(field)
            continue
        try:
            facts[field] = float(value) if "." in value else int(value)
        except ValueError:
            facts[field] = value
    facts["Recommended play"] = PLAYS[facts["Weakest dimension"]]
    return facts, gaps


def draft_brief(client, facts):
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(facts, indent=2, ensure_ascii=False)}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": BRIEF_SCHEMA}},
        # If a safety classifier declines, the API retries on a suitable fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        sys.exit("Claude declined to write this brief. Nothing saved.")
    if response.stop_reason == "max_tokens":
        sys.exit("The brief was cut off before it finished. Nothing saved.")
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)


NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers_in(text):
    return {float(n.replace(",", "")) for n in NUMBER.findall(text)}


def allowed_numbers(facts):
    """Every number the brief may use: the values, rates as percentages, and numbers inside labels and text."""
    allowed = set()
    for field, value in facts.items():
        allowed |= numbers_in(field)
        if isinstance(value, (int, float)):
            for n in (abs(value), abs(value) * 100):
                allowed |= {n, round(n), round(n, 1)}
        else:
            allowed |= numbers_in(value)
    return allowed


def check_brief(brief, facts):
    """Return a list of problems. An empty list means the brief can be saved."""
    problems = []
    prose = " ".join(
        [brief["headline"], brief["situation"], brief["next_step"], *brief["questions"]]
        + [risk["point"] for risk in brief["risks"]]
    )
    allowed = allowed_numbers(facts)
    for n in sorted(numbers_in(prose)):
        if not any(abs(n - a) < 1e-6 for a in allowed):
            problems.append(f"The number {n:g} isn't in the account data.")
    for risk in brief["risks"]:
        if not risk["evidence"]:
            problems.append(f"No evidence given for: {risk['point']}")
        for name in risk["evidence"]:
            if name not in facts:
                problems.append(f"Evidence {name!r} isn't a field in the account data.")
    return problems


def render(account, facts, gaps, brief):
    lines = [
        f"# Pre-call brief: {account}",
        "",
        f"{facts['Sector']} · {facts['Segment']} · {facts['Lifecycle stage']} · "
        f"£{facts['ARR (£)']:,} ARR · renews {facts['Renewal date']}",
        f"Health score {facts['Health score']} ({facts['Band']}). Alert: {facts['Alert']}.",
        "",
        f"**{brief['headline']}**",
        "",
        brief["situation"],
        "",
        "## Risks",
        *[f"- {r['point']} _(Evidence: {'; '.join(r['evidence'])})_" for r in brief["risks"]],
        "",
        "## Questions to ask",
        *[f"{i}. {q}" for i, q in enumerate(brief["questions"], 1)],
        "",
        "## Next step",
        brief["next_step"],
        "",
        "## Data gaps",
        ("No data for: " + "; ".join(gaps) + ". Ask about these rather than assume.") if gaps
        else "None. Every metric has data.",
        "",
        "_Drafted by Claude from the health score data, and checked: every number traces to the data._",
    ]
    return "\n".join(lines) + "\n"


def run(client, account, dry_run):
    facts, gaps = load_facts(account)
    if dry_run:
        print(f"--- System prompt ---\n{SYSTEM_PROMPT}\n\n--- Facts sent for {account} ---")
        print(json.dumps(facts, indent=2, ensure_ascii=False))
        print(f"\n--- Data gaps (added to the brief by code) ---\n{gaps or 'None'}")
        return True

    brief = draft_brief(client, facts)
    problems = check_brief(brief, facts)
    if problems:
        print(f"{account}: brief failed the check, so it wasn't saved.")
        for p in problems:
            print(f"  - {p}")
        return False

    OUTPUTS.mkdir(exist_ok=True)
    path = OUTPUTS / (re.sub(r"[^a-z0-9]+", "-", account.lower()).strip("-") + ".md")
    path.write_text(render(account, facts, gaps, brief), encoding="utf-8")
    print(f"{account}: saved {path}")
    return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # so £ prints correctly in the Windows terminal
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("account", nargs="?", help="account name, as in data/accounts.csv")
    parser.add_argument("--all", action="store_true", help="write a brief for every account")
    parser.add_argument("--dry-run", action="store_true", help="show what would be sent, without calling the API")
    args = parser.parse_args()
    if not args.account and not args.all:
        parser.error("name an account or use --all")

    accounts = list(read_csv("accounts.csv")) if args.all else [args.account]
    client = None
    if not args.dry_run:
        import anthropic  # only needed for a real API call, so --dry-run works without the package

        client = anthropic.Anthropic()
    results = [run(client, account, args.dry_run) for account in accounts]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
