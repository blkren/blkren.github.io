---
name: log-review
description: Review an AI agent's conversation logs for a service business after go-live. Flags quality issues, missed escalations, bypass and enterprise access problems, buckets them by value-chain stage, works out the resolution rate and correct handling rate, and drafts actions, bug reports and product feedback. Use during hypercare and in weekly reviews.
---

# Log review

You review conversation logs from an AI agent that answers calls and messages, books appointments and triages urgent requests for a regulated service business. You flag and classify; the go-live lead checks and decides what to fix.

## Inputs

1. **Sector pack** from `sector-packs/`, for its urgent triggers, always-human topics and compliance flags.
2. **Conversation log**: a CSV or table. Expected columns (adapt to the real export, and say which columns were missing):

| Column | Meaning |
|---|---|
| `conversation_id` | Unique ID |
| `site` | Site name (some exports call it `branch`) |
| `channel` | phone, email, messaging, portal, web chat |
| `timestamp` | Date and time |
| `out_of_hours` | true or false |
| `intent` | The sector pack's workflows, or other |
| `transcript` | What was said, or a summary |
| `outcome` | resolved, booked (for example viewing_booked, appointment_booked), job_raised, escalated, abandoned |
| `escalation_ack_minutes` | Minutes until a person picked up an escalation (blank if none) |
| `staff_override` | true if staff changed or redid what the AI did |
| `customer_ref` | Optional. A pseudonymous caller reference, used to spot repeat contact |

The log format above is an assumption for this kit. Replace it with the real schema.

3. Optional, for enterprise accounts: **admin and access logs** (sign-ins, user provisioning, access-denied events) and the signed-off site and role map.

## Rules

- Judge only from the log. If a flag depends on information you don't have (for example, the business's current prices), mark it `[CHECK: what to verify]`.
- **Critical** means a safety risk, a possible compliance breach, or a complaint, payment or dispute handled by the AI instead of a person.
- Never quote personal details in the summary. Refer to conversations by ID.
- UK English. No em dashes.

## Definitions

Use these two rates in every review, in this order, and never mix them up.

- **Resolution rate:** conversations with the right outcome, no staff involvement, no Quality or Outcomes flag, and no repeat contact from the same customer within 72 hours, divided by all conversations reviewed. This is the figure that feeds the health score (V2). If the log has no `customer_ref`, say that repeat contact couldn't be checked.
- **Correct handling rate:** resolutions, plus correct escalations (the AI handed over the right conversation to a person, even if the person was slow), plus outcomes staff redid where the AI was right (bypass). Divided by all conversations reviewed.
- The gap between the two is the cost of bypass and of hand-offs: work the AI did right that still needed a person. Say how big it is and what it's made of.
- "Outcome reached" (resolved, booked or job raised) is a separate count. Report it, but never call it a resolution rate.

## Step 1: Classify each conversation

For each conversation, record:

- **Flags** (zero or more):
  - `wrong_info`: an answer that looks incorrect or invented
  - `missed_escalation`: should have gone to a person and didn't
  - `unsafe_handling`: an urgent trigger from the sector pack not treated as urgent
  - `compliance_risk`: wording or handling that hits one of the sector pack's compliance flags
  - `booking_failure`: tried to book and failed, or booked outside agreed windows
  - `slow_pickup`: escalation picked up later than the agreed time (default 30 minutes if not given)
  - `bypass`: staff override or redo where the AI's handling was fine
  - `abandoned`: the person dropped off before an outcome
- **Bucket** of the main issue: Coverage, Quality, Adoption, Outcomes or Evidence
- **Severity**: Critical, High, Medium, Low
- **Fix type**: Set-up (fixed by the go-live lead), Data (fixed by the business with the go-live lead), User (training) or Product (engineering)
- **Counts as**: resolution, correct escalation, correct but redone, or neither

## Step 2: Enterprise failure signals (if admin and access logs are supplied)

Look for:

- **Failed sign-ins**, clustered by site or role. Many at one site usually means single sign-on isn't set up for that group.
- **Users still active who should have been removed** (leavers). This means automatic provisioning and removal isn't working.
- **Access-denied errors**: staff blocked from records the site and role map says they should see, or the reverse.
- **Staff working outside the tool**: bookings or messages in the system of record with no matching AI agent conversation, or shared logins.

Each is an Adoption issue (staff can't or don't use the tool) unless it exposes data to the wrong person, which is Quality and Critical. If the cause is a gap in the product rather than the set-up, write it up as **product feedback**: the gap, the account, its ARR, its lifecycle stage, and what it blocks.

## Step 3: Summarise

1. **Headline:** conversations reviewed; outcome reached; resolution rate; correct handling rate and the gap between them; critical flags; out-of-hours share.
2. **By bucket:** count of issues per bucket, and what that suggests.
3. **Clusters:** group repeated issues (same intent, same flag, same site). Rank by severity, then frequency.
4. **Outcomes for the value ledger:** bookings made, jobs raised, requests captured, out of hours versus in hours.
5. **Actions:** for each cluster, the fix type, the owner and the next step. Every Set-up fix also adds a scenario to the test suite.
6. **Bug reports:** for each Product issue, a draft with title, steps to reproduce (from the log), expected versus actual, conversations affected, sites affected, severity.
7. **Product feedback:** enterprise or capability gaps, with account, ARR and lifecycle stage.
8. **Template candidates:** set-up fixes that have happened twice or more, across this or other customers, which should become templates or sector pack defaults.
9. **Gate check:** did any failure match a scenario already in the test suite? If so, say whether the gate was run and passed before this stage started.

## Output

One markdown report in the order above, opening with a three-line summary: overall quality (Red, Amber or Green), the top issue, and the one action to take this week.
