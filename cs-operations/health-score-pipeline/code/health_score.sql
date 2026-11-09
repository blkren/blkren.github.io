-- Customer health score, in SQL.
-- The same rules as the Inputs sheet in health_score_model.xlsx, so the
-- results match the Excel model account for account.
-- Expects a table called `accounts` with the columns in data/accounts.csv.

DROP VIEW IF EXISTS scored_accounts;

CREATE VIEW scored_accounts AS
WITH signals AS (
  SELECT
    a.*,
    CASE WHEN workflows_contracted > 0
         THEN 1.0 * workflows_live / workflows_contracted
         ELSE 0 END AS utilisation
  FROM accounts a
),

-- Each signal scored 0 to 10 against the thresholds on the Inputs sheet.
signal_scores AS (
  SELECT
    s.*,
    CASE WHEN utilisation >= 0.9 THEN 10
         WHEN utilisation >= 0.7 THEN 7
         WHEN utilisation >= 0.5 THEN 5
         WHEN utilisation >= 0.3 THEN 3
         ELSE 1 END AS s_utilisation,
    CASE WHEN days_since_admin_login <= 7  THEN 10
         WHEN days_since_admin_login <= 14 THEN 8
         WHEN days_since_admin_login <= 30 THEN 5
         WHEN days_since_admin_login <= 60 THEN 3
         ELSE 1 END AS s_admin_login,
    CASE WHEN ai_features_used = 'Y' THEN 10 ELSE 4 END AS s_ai_features,
    customer_pulse_1to5 * 2 AS s_pulse,
    CASE WHEN days_since_client_engaged <= 30  THEN 10
         WHEN days_since_client_engaged <= 60  THEN 7
         WHEN days_since_client_engaged <= 90  THEN 4
         WHEN days_since_client_engaged <= 120 THEN 2
         ELSE 1 END AS s_client_engaged,
    CASE WHEN days_since_we_contacted <= 30  THEN 10
         WHEN days_since_we_contacted <= 60  THEN 7
         WHEN days_since_we_contacted <= 90  THEN 4
         WHEN days_since_we_contacted <= 120 THEN 2
         ELSE 1 END AS s_we_contacted,
    -- Sponsor, champion and 2+ admins are each worth a third of 10.
    10.0 / 3 * ((exec_sponsor = 'Y') + (champion = 'Y') + (admin_users >= 2)) AS s_contacts,
    CASE WHEN open_tickets = 0 THEN 10
         WHEN open_tickets <= 2 THEN 7
         WHEN open_tickets <= 5 THEN 4
         WHEN open_tickets <= 8 THEN 2
         ELSE 1 END AS s_open_tickets,
    CASE WHEN escalated_tickets = 0 THEN 10
         WHEN escalated_tickets <= 1 THEN 5
         WHEN escalated_tickets <= 2 THEN 2
         WHEN escalated_tickets <= 3 THEN 1
         ELSE 0 END AS s_escalations,
    CASE WHEN payment_overdue = 'Y' THEN 2 ELSE 10 END AS s_payment
  FROM signals s
),

-- Dimensions: adoption 35%, relationship 35%, support 15%, commercial 15%.
raw AS (
  SELECT
    ss.*,
    0.35 * (0.5 * s_utilisation + 0.3 * s_admin_login + 0.2 * s_ai_features)
  + 0.35 * (0.35 * s_pulse + 0.25 * s_client_engaged + 0.15 * s_we_contacted + 0.25 * s_contacts)
  + 0.15 * (0.4 * s_open_tickets + 0.6 * s_escalations)
  + 0.15 * s_payment AS raw_score,
    -- Hard cap: an overdue payment or 2+ escalations caps the score at 6.
    (payment_overdue = 'Y' OR escalated_tickets >= 2) AS capped
  FROM signal_scores ss
),

scored AS (
  SELECT
    r.*,
    -- The tiny nudge makes a raw 3.25 round to 3.3 as it does in Excel,
    -- even if floating-point maths lands on 3.2499999...
    ROUND(CASE WHEN capped AND raw_score > 6 THEN 6 ELSE raw_score END + 1e-9, 1) AS health_score
  FROM raw r
),

banded AS (
  SELECT
    sc.*,
    CASE WHEN health_score < 5 THEN 'Red'
         WHEN health_score < 7 THEN 'Amber'
         WHEN health_score < 9 THEN 'Light green'
         ELSE 'Dark green' END AS band,
    CASE WHEN days_to_renewal <= 90  THEN 1.5
         WHEN days_to_renewal <= 180 THEN 1.2
         ELSE 1.0 END AS urgency
  FROM scored sc
)

SELECT
  account_id,
  account_name,
  segment,
  arr_gbp,
  days_to_renewal,
  ROUND(utilisation, 3) AS utilisation,
  ROUND(raw_score, 3) AS raw_score,
  capped,
  health_score,
  band,
  -- Who to call first: ARR at risk, weighted by how soon they renew. Red and amber only.
  CASE WHEN band IN ('Red', 'Amber')
       THEN ROUND(arr_gbp * (10 - health_score) / 10 * urgency, 2)
       ELSE 0 END AS priority,
  (health_score >= 8 AND (utilisation >= 0.9 OR growth_signal = 'Y')) AS expansion_candidate,
  CASE band
    WHEN 'Red' THEN CASE segment
      WHEN 'Enterprise' THEN 'Review account; executive call within 5 working days; agree a joint recovery plan'
      WHEN 'Mid-market' THEN 'Review account; check-in call within 5 working days; recovery plan'
      ELSE 'Review account; check-in call within 10 working days; send targeted self-help resources' END
    WHEN 'Amber' THEN CASE segment
      WHEN 'Enterprise' THEN 'Review account; executive call if renewal is within 120 days, otherwise check-in within 2 weeks'
      WHEN 'Mid-market' THEN 'Review account; check-in within 2 weeks'
      ELSE 'Review account; targeted tech-touch sequence; call if no response' END
    WHEN 'Light green' THEN CASE segment
      WHEN 'Enterprise' THEN 'Keep cadence; QBR and success plan review'
      WHEN 'Mid-market' THEN 'Keep cadence; success plan review'
      ELSE 'Tech-touch nurture; best-practice content' END
    ELSE CASE segment
      WHEN 'Enterprise' THEN 'Expansion conversation; advocacy ask (case study or reference)'
      WHEN 'Mid-market' THEN 'Expansion conversation; advocacy ask'
      ELSE 'Upsell offer via tech touch; review or referral ask' END
  END AS recommended_play
FROM banded;


-- Week-on-week changes: compares this run with the previous run in score_history.
DROP VIEW IF EXISTS score_changes;

CREATE VIEW score_changes AS
WITH runs AS (
  SELECT DISTINCT run_date FROM score_history ORDER BY run_date DESC LIMIT 2
),
this_run AS (SELECT * FROM score_history WHERE run_date = (SELECT MAX(run_date) FROM runs)),
last_run AS (SELECT * FROM score_history WHERE run_date = (SELECT MIN(run_date) FROM runs)
                                            AND (SELECT COUNT(*) FROM runs) = 2)
SELECT
  t.account_id,
  t.account_name,
  t.arr_gbp,
  l.health_score AS previous_score,
  t.health_score AS current_score,
  ROUND(t.health_score - l.health_score, 1) AS change,
  l.band AS previous_band,
  t.band AS current_band,
  CASE
    WHEN t.band IN ('Red', 'Amber') AND l.band NOT IN ('Red', 'Amber') THEN 'Moved into red or amber'
    WHEN t.health_score - l.health_score <= -1.0 THEN 'Dropped 1 point or more'
    WHEN t.capped AND NOT l.capped THEN 'Newly capped (payment or escalations)'
  END AS alert
FROM this_run t
JOIN last_run l USING (account_id)
WHERE t.band IN ('Red', 'Amber') AND l.band NOT IN ('Red', 'Amber')
   OR t.health_score - l.health_score <= -1.0
   OR (t.capped AND NOT l.capped);
