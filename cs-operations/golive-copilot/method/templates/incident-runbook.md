# Incident runbook

What to do when the AI agent gets something seriously wrong in production.

## Severity

| Severity | Definition | Examples | Response |
|---|---|---|---|
| Critical | Safety risk, possible compliance breach, data shown to the wrong person, or a complaint, payment or dispute handled by the AI instead of a person | Urgent trigger treated as routine; clinical advice given; a blanket-ban rule applied | Pause the use case now; use the switch below if needed |
| High | Lost revenue or a wrong answer to a customer, with no safety risk | Leads abandoned because no slots were offered; wrong price quoted | Fix within 2 working days |
| Medium | Poor experience or staff workaround | Slow escalation pick-up; staff redoing bookings | Fix within the next review cycle |
| Low | Cosmetic | Wording, tone | Batch with the next change |

## The switch: everything to a person

Every go-live has a tested way to route all calls and messages straight to staff, and the go-live lead and the business's champion both know how to use it. Test it before stage 1. Use it when a Critical incident can't be contained by pausing one use case.

## Who's told and when

| When | Who | How |
|---|---|---|
| Within 1 hour of a Critical | Business's decision maker and champion; engineering on-call; my manager | Phone, then written |
| Within 1 working day | Account owner in Sales; Product | Written summary |
| Within 5 working days | The business | Written explanation (below) |

## Steps

1. **Contain.** Pause the use case, or use the switch. Make sure any affected customer is contacted by a person.
2. **Root cause.** Set-up, Data, User or Product. Find the configuration version that was live.
3. **Fix.** Change the configuration, data or training. Product issues get a bug report with severity and affected accounts.
4. **Retest.** Run the full suite against the fix. The gate must be met.
5. **New test.** Add the failure as a scenario to the test suite, marked safety or escalation if it was one.
6. **Written explanation to the customer.** What happened, who was affected, what we did straight away, the cause, the fix, the new test, and what we'll watch. No jargon, no blame.
7. **Log it.** In the config change log, and in the account's health score as a critical incident if it was Critical.
8. **Restart.** Resume the paused use case at the previous rollout stage, not where it was.
