# Pre-call brief: Fenwick Gas Services

> Illustrative example, written by hand from Fenwick's data to show the output format. A real run is worded differently. Every number here is in the data, so it would pass the check.

Heating and plumbing · Mid-market · Adoption · £60,000 ARR · renews 2027-05-01
Health score 49 (At risk). Alert: Red flag (critical safety incident; would be 73).

**A critical safety incident in the last 30 days has capped Fenwick at 49. Without it the score would be 73.**

Fenwick is a mid-market heating and plumbing customer in the Adoption stage, worth £60,000 a year and renewing on 2027-05-01. The score fell 21 points from 70. Outside AI quality the account looks solid: an 80% AI resolution rate, 80% coverage of eligible work, champion strength of 4 out of 5 and an NPS of 30.

## Risks
- Critical errors are running at 4.5 per 1,000 tasks, and one of them was a safety or compliance incident. A repeat would be hard to recover from. _(Evidence: Flag: critical safety or compliance incident (30 days); Q1 Critical errors per 1,000 tasks)_
- 90% of escalations are picked up within SLA, so some urgent hand-offs still wait too long. For a gas engineer, that is where an emergency gets missed. _(Evidence: Q3 Escalations picked up within SLA)_
- Staff may stop trusting the agent after the incident. The override rate is 10% today: watch it weekly. _(Evidence: Q2 Human override / edit rate)_

## Questions to ask
1. What happened on the call that caused the incident, and has your team changed how they use the agent since?
2. Who on your side needs to see the fix before they're comfortable again?
3. When the agent flags an emergency today, how quickly does a person pick it up?

## Next step
Run a quality escalation: review the error with Product, fix the top three error patterns, confirm the hand-off time, then walk the champion through the fix.

## Data gaps
None. Every metric has data.
