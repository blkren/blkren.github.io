# How go-live outputs feed the health score

The go-live kit and the [AI agent health score](../../../retention-and-churn/ai-agent-health-score/) measure the same things, so a go-live hands over a working set of metrics, not a blank account. The [pre-call account brief generator](../../../ai-workflows/account-brief-generator/) then turns those metrics into a brief for the CSM's next call.

| Go-live output | Where it comes from in the kit | Health score input |
|---|---|---|
| Coverage: eligible requests the AI agent handles, out of all eligible requests. Shadow-stage drafts don't count | Phased rollout plan; channel logs | **A1** Coverage of eligible work |
| Bypass: requests staff handled around the AI agent, or work it did that staff redid | `log-review` (`bypass` flag); channel logs against AI intake | **A2** Bypass rate |
| Critical errors per 1,000 tasks | `log-review` (Critical severity); incident runbook | **Q1** Critical errors per 1,000 tasks |
| Escalations picked up within the agreed time | `log-review` (`slow_pickup` flag, `escalation_ack_minutes`) | **Q3** Escalations picked up within SLA |
| Days from contract start to the first stage delivering value (stage 1 live) | Phased rollout plan | **F1** Time to first value |
| Share of configuration changes that failed in production | Config change log | **F4** Configuration change failure rate |
| Resolution rate | `log-review` | **V2** AI resolution rate |

## Definitions

- **Resolution rate (V2):** conversations with the right outcome, no staff involvement, no Quality or Outcomes flag, and no repeat contact within 72 hours, divided by all conversations.
- **Correct handling rate:** resolutions, plus correct escalations, plus outcomes staff redid where the AI was right, divided by all conversations. It isn't a health score input. I report it next to V2 because the gap between the two is the cost of bypass, and it tells me whether a low V2 is an AI problem or a trust problem.
- "Outcome reached" is not a resolution. An outcome can be wrong.

## The two samples

| Input | Kestrel Row, week 1 | Brightwater Clinics, 29 October 2026 |
|---|---|---|
| A1 Coverage | Not measured (no channel logs) | 45% |
| A2 Bypass | 2 of 12 conversations redone by staff | Not measured yet |
| Q1 Critical errors | 2 in 12 conversations | 2 per 1,000 tasks |
| Q3 Escalations on time | 1 of 2 within 30 minutes | 75% within 15 minutes |
| F1 Time to first value | Not recorded | 50 days |
| F4 Change failure rate | No change log | 25% (2 of 8) |
| V2 Resolution rate | 17% (2 of 12) | 68% |
| Correct handling rate | 50% (6 of 12) | 81% |

Kestrel Row's figures come from 12 conversations, too few for a reliable rate. They're shown to make the definitions concrete. Brightwater's figures match its row in the health score dataset.

## Why it matters

- **Missing data stays missing.** If the go-live didn't set up a measure (Kestrel Row had no channel logs, so no coverage figure), the health score treats it as a gap that lowers confidence, not as zero.
- **A go-live that's mid-rollout reads correctly.** Brightwater's 45% coverage and 40% use cases live are where the rollout plan says they should be. The health score puts adoption first in onboarding, so it flags the account for an adoption sprint, which matches the go-live pack's own blockers.
- **Gates and the score use the same numbers.** The stage 1 exit gate (escalations picked up on time) is the same figure as Q3, so a failed gate and a falling score are never telling different stories.
