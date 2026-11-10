# Configuration change log

Every change to the AI agent's configuration is logged here: knowledge base, rules, routing, integrations, channels. No change goes live without a test rerun.

This log feeds the health score's **configuration change failure rate (F4)**: the share of changes that caused a failure in production or had to be rolled back. A high rate means changes are going out without enough testing.

| Version | Date | Change | Reason | Tests rerun | Result | Rollback path | Failed in production? |
|---|---|---|---|---|---|---|---|
| v1.0 | | Initial configuration | Go-live | Full suite | x of y passed | n/a | |
| v1.1 | | | | | | | |

## Rules

- **One change per version** where possible, so a failure can be traced.
- **Tests rerun:** at least the safety and escalation scenarios, plus every scenario the change touches. A change to urgent routing reruns the full suite.
- **Result** must meet the gate in `test-suite-and-gate.md` before the change goes live.
- **Rollback path:** the version to go back to and how long it takes.
- **Failed in production?** Fill in after a week. Yes if it caused an incident, a log-review flag or a rollback.

## F4 calculation

Configuration change failure rate = changes marked "Failed in production? Yes" / all changes in the period.
