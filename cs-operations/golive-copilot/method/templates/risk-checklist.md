# Go-live risk checklist

Risks are grouped by the five things that must be true for a business to keep paying for an AI agent. Grouping them this way shows patterns across customers: if most go-lives go red on Coverage, fix the onboarding playbook; if most go red on Adoption, fix training and champions.

Score each: Red (blocks go-live), Amber (fix within 14 days), Green (ready).

Risks 1 to 13 keep their original numbers, so older go-live packs still match. Risks added later are numbered from 14 and listed under their bucket.

| Bucket | # | Risk | What Red looks like |
|---|---|---|---|
| **1. Coverage** (the AI sees the requests) | 1 | Call forwarding | Overflow-only or no forwarding, so the AI misses most calls |
| | 2 | Channel gaps | A lead source, messaging channel or inbox not routed |
| | 3 | System of record access | No credentials, or one-way sync only |
| | 4 | Upcoming change | System migration, site opening or merger during go-live |
| **2. Quality** (the AI handles them correctly) | 5 | Knowledge base | Prices, policies or services missing or out of date |
| | 6 | Compliance rules | Rules that hit the sector pack's compliance flags |
| | 7 | Urgent requests | No named emergency contact or routing for urgent triggers |
| | 19 | Access model | Access doesn't match the signed-off site and role map |
| | 20 | Data processing and retention | No signed data processing agreement, or retention not set |
| | 21 | Test gate | Test suite not run, or below the gate, before a stage starts |
| **3. Adoption** (staff rely on it) | 8 | Champion | No named champion, or champion is sceptical |
| | 9 | Escalation cover | One contact for all sites; no weekend rota |
| | 10 | Staff bypass | Signs staff will answer first or work around the AI |
| | 14 | Fear of replacement | Staff believe the AI agent is there to replace them, and nobody has told them otherwise |
| | 15 | Scepticism | Staff expect it to fail and are looking for proof |
| | 16 | Single point of knowledge | One person holds rules or answers nobody else knows |
| | 17 | Influential sceptic | Someone others listen to is against it |
| | 18 | Staff not consulted | Fewer than five staff interviewed, or a site in the next stage with nobody interviewed |
| | 22 | Sign-in and provisioning | No single sign-on, or leavers keep access |
| **4. Outcomes** (it changes business results) | 11 | Follow-through | Bookings made but no one owns delivering them |
| **5. Evidence** (the owner can see it) | 12 | Trial discipline | Success criteria, go-live date or price not agreed in writing |
| | 13 | Baseline | No before figures to prove value |
| | 23 | Audit logs | The business can't see who did what, so value and incidents can't be shown |

People risks (14 to 18) are scored from the staff interviews and tracked in `people-risk-register.md`.

## Cross-customer view

Keep a running table of every go-live's ratings by bucket. Review it monthly: the bucket that goes red most often is where to invest in templates, training or product fixes.

| Customer | Sector | Coverage | Quality | Adoption | Outcomes | Evidence |
|---|---|---|---|---|---|---|
| Kestrel Row Lettings (sample) | Lettings | Red | Red | Red | Amber | Red |
| Brightwater Clinics (sample, mid-rollout) | Health clinics | Amber | Amber | Red | Amber | Amber |
