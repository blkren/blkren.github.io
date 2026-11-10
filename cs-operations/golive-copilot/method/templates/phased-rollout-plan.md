# Phased rollout plan

A phased, cohort-based rollout where each stage proves value before the next. A stage only starts when the one before has met its exit gate.

## Why phase it

A big-bang launch across every site and channel puts all the risk on day one. If something goes wrong, such as an urgent request missed or a wrong answer to a customer, staff see it everywhere at once, and the story becomes "AI is overrated". Phasing builds trust stage by stage: staff see the AI agent work on a small scope first, problems are found where they're cheap to fix, and each gate gives the decision maker evidence, not promises.

## Stages

| Stage | What runs | Exit gate | Rollback trigger | Owner |
|---|---|---|---|---|
| 0. Shadow | AI drafts, staff send | Test set passed; staff rate answers usable | Any critical safety or compliance error pauses that use case | Go-live lead |
| 1. One site, out of hours | AI handles evenings and weekends | 2 weeks, no critical errors, escalations picked up on time | Any critical safety or compliance error pauses that use case | Go-live lead, site lead |
| 2. Overflow in hours | AI takes unanswered calls | Bypass below target; champion signs off | Any critical safety or compliance error pauses that use case | Champion |
| 3. All channels, all sites | Full coverage | Value review shows a gain against baseline | Any critical safety or compliance error pauses that use case | Decision maker, go-live lead |
| 4. New use cases | e.g. maintenance, valuations, recalls | That use case's own tests passed | Any critical safety or compliance error pauses that use case | Go-live lead |

## Rules

- **Gates, not dates.** A date in the contract is a target. The gate decides.
- **Cohorts.** Sites move through the stages in cohorts. The first cohort is the site with the strongest champion, not the biggest.
- **Use cases move separately.** A use case with no named urgent contact stays at stage 0 even if others move on.
- **Rollback is to the previous stage for that use case only.** Other use cases keep running.
- **Every rollback adds a test.** The failure becomes a scenario in the test suite before the stage is retried.

## Plan for this customer

| Cohort | Sites | Use cases | Current stage | Next gate | Target date | Gate evidence |
|---|---|---|---|---|---|---|
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

## Targets agreed with the customer

| Measure | Target | Source of the figure |
|---|---|---|
| Escalations picked up within | [minutes] | Escalation log |
| Bypass rate below | [%] | Channel logs against AI intake |
| Resolution rate at least | [%] | Log review |
| Value gain against baseline | [figure] | Value baseline |
