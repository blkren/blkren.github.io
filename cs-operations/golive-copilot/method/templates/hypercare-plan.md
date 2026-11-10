# Hypercare plan

The period straight after each stage goes live, when problems are most likely and cheapest to fix.

## Cadence

| Period | What happens | Who |
|---|---|---|
| Days 1 to 14 | **Daily log review** with the `log-review` skill. Critical flags acted on the same day. 15-minute check-in with the champion | Go-live lead, champion |
| Day 7 | First value snapshot against the baseline | Go-live lead |
| Day 14 | Stage gate review: does this stage meet its exit gate? | Go-live lead, decision maker |
| Weeks 3 to 6 | **Weekly log review.** Weekly value summary to the decision maker | Go-live lead |
| Week 6 | Hypercare exit review | Go-live lead, decision maker, CSM |

## Daily check

- Critical flags: any? Contained?
- Escalations picked up on time?
- Abandoned conversations and why
- Bypass: which staff, which site, why
- Config changes made yesterday: rerun results

## Exit criteria

Hypercare ends when all are true for two weeks in a row:

- No critical errors
- Escalations picked up within the agreed time at least 95% of the time
- Bypass rate below the target in the rollout plan
- Resolution rate at or above target
- No open High issues older than 5 working days
- Test suite passing at the gate after the latest change

## Handover to business as usual

- Weekly log reviews move to monthly, owned by the CSM.
- Open issues handed over with owners and dates.
- Health score metrics confirmed as feeding correctly (see `../health-score-mapping.md`).
- Next rollout stage and its gate written into the account plan.
- Lessons that apply to other customers go into templates or the sector pack.
