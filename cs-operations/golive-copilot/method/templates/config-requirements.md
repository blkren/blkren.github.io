# Configuration requirements template

Every field: value + source, or `[MISSING]`. Add the sector pack's own fields under section 4.

## 1. Integrations
- System of record and connection method:
- Two-way sync confirmed (tested, not assumed):
- Calendar or diary used for bookings:
- Behaviour when the system of record is down:

## 2. Channels
- Phone forwarding mode (all calls / overflow / out of hours only):
- Numbers per site:
- Email inboxes to route:
- Web chat, messaging apps and SMS status:
- Other lead sources (for example property portals):

## 3. Site knowledge base (one per site)
- Opening hours:
- Areas or services covered:
- Prices and fees:
- Policies (deposits, cancellations, pets, warranties):
- Booking rules (who, which windows, lead time, length):

## 4. Sector fields
- (From the sector pack)

## 5. Qualification and identity
- Questions the AI agent asks:
- Identity checks before discussing an existing record:
- Rules flagged by the sector pack's compliance checks:

## 6. Urgent requests
- Urgent triggers (from the sector pack, plus any the business adds):
- Response for each:
- Named emergency contact, in hours:
- Named emergency contact, out of hours and weekends:

## 7. Escalations
- Named contact per site (in hours):
- Out-of-hours and weekend rota:
- Pick-up time agreed:
- Warm transfer to a person available (Y/N, which numbers):
- Topics always handed to a person:

## 8. AI disclosure
- Disclosure wording:
- Approved by:

## 9. Enterprise readiness
Required for enterprise accounts; check for any account with more than one site.

| Check | How it's tested | Result |
|---|---|---|
| Single sign-on | Every role signs in through the business's identity provider; no local passwords | |
| Automatic user provisioning and removal (SCIM) | Add a test starter and remove a **test leaver**; the leaver loses access within the agreed time | |
| Access model matches the signed-off site and role map (ABAC) | Sign in as each role at two sites; each sees only what the map allows | |
| Data processing agreement signed | Copy on file, with the date | |
| Retention settings | Transcripts and recordings deleted after the agreed period; tested on a sample | |
| Audit logs | Sign-ins, configuration changes and data exports are logged and the business can see them | |

A failed check caused by a product gap becomes product feedback with the account, ARR and lifecycle stage.

## 10. Reporting
- Baseline captured (Y/N, which figures):
- Who receives the weekly value summary:
