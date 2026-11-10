# People risk register

Most AI agent go-lives that fail, fail on people, not configuration. This register tracks the people risks found in discovery interviews, the same way the risk checklist tracks technical ones. It maps to risks 14 to 18 under Adoption in `risk-checklist.md`.

Score each: Red (blocks the next stage), Amber (act within 14 days), Green (no action needed).

| # | Risk | What to look for | Evidence | Rating | Action | Owner | Review date |
|---|---|---|---|---|---|---|---|
| 14 | Fear of replacement | "Is this taking my job?"; people going quiet when the AI agent comes up; front-desk staff asking about hours | | | Honest role-change message from the decision maker; show what stays human; involve them in testing | Decision maker, go-live lead | |
| 15 | Scepticism | "It'll get it wrong"; past tools that failed; staff collecting examples of mistakes | | | Shadow stage where they rate the AI's drafts; share test results; fix what they find and tell them | Go-live lead | |
| 16 | Single point of knowledge | "Only X knows that"; rules held in one person's head or spreadsheet | | | Capture their knowledge in the knowledge base first; give them a reviewer role | Go-live lead, that person | |
| 17 | Influential sceptic | Someone others go to for answers who is against it | | | Meet them one to one; ask them to break it in testing; give their objections a written answer | Go-live lead, champion | |
| 18 | Staff not consulted | Fewer than five interviews, or a site in the next stage, or a role, with nobody interviewed | | | Interview more people before the stage gate | Go-live lead | |

## How to rate

- **Red:** the risk is present and has no owner or action yet, or it sits with someone the next stage depends on.
- **Amber:** present, with an action agreed but not done.
- **Green:** not present, or the action is done and the evidence has changed.

## Rules

- Evidence comes from interviews, using themes, not quotes, unless the person agreed.
- A Red people risk blocks the next rollout stage, like any other Red.
- Review the register at each stage gate.
