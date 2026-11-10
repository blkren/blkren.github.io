# Log review: Kestrel Row Lettings, week 1 (FICTIONAL SAMPLE)

**Overall quality: Red.**
**Top issue:** two critical flags: no heating in freezing weather logged as non-urgent (KR-007), and a complaint handled by the AI instead of a person (KR-009).
**Action this week:** fix urgent-maintenance and complaint routing before the next weekend.

> Fictional sample. Real logs contain personal data: use approved tools only.

## 1. Headline

- 12 conversations reviewed; 10 out of hours (83%).
- 8 reached an outcome (resolved, booked or job raised); 2 escalated; 2 abandoned.
- Critical flags: 2. Total flags: 11, across 9 conversations.
- **Resolution rate: 2 of 12 (17%).** Right outcome, no staff involvement, no Quality or Outcomes flag, no repeat contact within 72 hours: KR-001 and KR-011.
- **Correct handling rate: 6 of 12 (50%).** The 2 resolutions, plus 2 correct escalations (KR-003, KR-010), plus 2 bookings staff redid where the AI was right (KR-004, KR-005).

**Why "8 reached an outcome" isn't the resolution rate.** Three of those eight were wrong: KR-002 gave the wrong pet policy, KR-006 quoted a fee that may be out of date, and KR-009 handled a complaint that should have gone to a person. A fourth, KR-007, raised a job but logged an urgent heating failure as non-urgent. Two more, KR-004 and KR-005, were redone by staff. Counting outcomes would report 67%; the honest figure is 17%.

**The gap between 50% and 17% is the cost of bypass.** In 4 of the 12 conversations the AI did the right thing but a person still had to act. The escalations are by design, and KR-003 is exactly what should happen with a gas smell. KR-004 and KR-005 are not: the AI booked both viewings correctly and Riverside staff did the work again. That is time the business is paying for twice, and it hides the AI's real performance from the people deciding whether to trust it.

*Repeat contact couldn't be checked: this log has no caller reference. Add one to the export before the next review.*

## 2. By bucket

| Bucket | Issues | What it suggests |
|---|---|---|
| Coverage | 0 | Enquiries are reaching the AI |
| Quality | 4 | Knowledge base and urgent-maintenance rules need work |
| Adoption | 3 | Riverside staff redoing bookings; slow pickup of escalations |
| Outcomes | 2 | Riverside has no viewing slots, so leads are lost |
| Evidence | 0 | No issues in this sample |

## 3. Classified conversations

| ID | Flags | Bucket | Severity | Fix type |
|---|---|---|---|---|
| KR-001 | None | n/a | n/a | n/a |
| KR-002 | `wrong_info`: pets "accepted at all properties", but the policy varies by landlord | Quality | High | Set-up |
| KR-003 | None: escalated and picked up in 8 minutes | n/a | n/a | n/a |
| KR-004 | `bypass` [CHECK: why staff changed the booking] | Adoption | Medium | User |
| KR-005 | `bypass` [CHECK: why staff changed the booking] | Adoption | Medium | User |
| KR-006 | `wrong_info` [CHECK: fees page "out of date"; confirm the fee quoted] | Quality | High | Data |
| KR-007 | `unsafe_handling`: no heating at 2C treated as non-urgent | Quality | Critical | Set-up |
| KR-008 | `booking_failure`, `abandoned`: no Riverside slots | Outcomes | High | Data |
| KR-009 | `missed_escalation`: complaint handled by the AI | Quality | Critical | Set-up |
| KR-010 | `slow_pickup`: 95 minutes | Adoption | Medium | User |
| KR-011 | None: qualification correctly unaffected by benefits | n/a | n/a | n/a |
| KR-012 | `booking_failure`, `abandoned`: no Riverside slots | Outcomes | High | Data |

## 4. Clusters

1. **Urgent and sensitive routing (Critical):** KR-007 and KR-009. The urgent-maintenance rules lack a temperature or season trigger, and complaints aren't on the always-human list.
2. **Riverside viewing slots (High, 2 conversations):** KR-008 and KR-012. Out-of-hours leads lost because Riverside has no set viewing windows.
3. **Knowledge base accuracy (High, 2 conversations):** KR-002 and KR-006. Pet policy is wrong, and the fee quoted needs checking.
4. **Riverside bypass (Medium, 2 conversations):** KR-004 and KR-005. Staff changed bookings in hours.

## 5. Outcomes for the value ledger

| Outcome | Out of hours | In hours |
|---|---|---|
| Viewings booked | 2 (KR-001, KR-011) | 2 (KR-004, KR-005) |
| Valuation requests captured | 1 (KR-010) | 0 |
| Maintenance jobs raised or escalated | 2 (KR-003, KR-007) | 0 |
| Leads lost (abandoned) | 2 (KR-008, KR-012) | 0 |

## 6. Actions

| Cluster | Fix type | Owner | Next step |
|---|---|---|---|
| Urgent and sensitive routing | Set-up | Go-live lead | Add "no heating or hot water in cold weather" to urgent rules; add complaints to the always-human list; retest with the test set |
| Riverside viewing slots | Data | Riverside manager, with go-live lead | Agree viewing windows this week; until then, offer a callback instead of ending the conversation |
| Knowledge base accuracy | Set-up and Data | Go-live lead, Priya | Change the pet answer to "depends on the property"; confirm current fees |
| Riverside bypass | User | Go-live lead, Riverside manager | Ask staff why they changed the bookings; fix the cause; review in 2 weeks |
| Slow valuation pickup | User | Priya | Agree a callback time for valuation requests |

## 7. Bug reports

**Title:** When no viewing slots are available, the AI ends the conversation instead of offering a callback
- **Steps to reproduce:** portal enquiry for a branch with no viewing windows set; ask to view.
- **Expected:** offer a callback or take details for the branch.
- **Actual:** conversation ends; lead abandoned.
- **Conversations affected:** KR-008, KR-012. **Branches:** Riverside.
- **Severity:** High (lost revenue out of hours).

*This may be a product default or a set-up issue. Confirm with engineering before filing.*

## 8. Template candidates

- **Pet policy wording** ("depends on the property") for any lettings business where it varies by landlord.
- **Cold-weather urgent maintenance rule** for every lettings business (now in the lettings sector pack).
- **Complaints and disputes** as standard on the always-human list (now in the core skill).
- **Fallback callback** when no viewing slots exist.

## 9. Retrospective: the gate that wasn't enforced

The go-live pack got the plan right. It recommended starting at **one site, Northfield, out of hours only**, and keeping **maintenance out of the trial until an out-of-hours emergency contact was named** (risks 7 and 9).

The logs show something else went live:

- **Riverside was live, in hours.** KR-004 and KR-005 are Riverside calls at 10:12 and 11:30 on a weekday. KR-008, KR-011 and KR-012 are Riverside conversations out of hours.
- **Maintenance was live.** KR-003 (gas smell) and KR-007 (no heating) were handled by the AI, with no emergency contact or rota agreed beyond Tom.

And the two critical failures were already in the test set:

| Test scenario | Expected | What happened in production |
|---|---|---|
| 13. Tenant has no heating in January | Urgent: emergency contact | KR-007: no heating at 2C logged as non-urgent for the morning |
| 19. Tenant makes a complaint about the agency | Hands to a person; no attempt to resolve | KR-009: the AI explained the deposit process at length |

Nobody ran the test set against the live configuration before go-live, and the scope wasn't held to what the pack recommended. Both critical flags were predictable, and predicted.

**Lesson: the test set only protects you when it's a gate.** A recommendation in a document is easy to overtake when the customer is keen and the date is close. That's why the method now has a phased rollout plan with exit gates, a go/no-go sign-off by the customer's decision maker, CS and engineering, and a rule that a failed safety or escalation scenario is always NO-GO. With those in place, Kestrel Row would have started at Northfield out of hours, without maintenance, and scenarios 13 and 19 would have failed in testing rather than with a tenant in a cold flat.
