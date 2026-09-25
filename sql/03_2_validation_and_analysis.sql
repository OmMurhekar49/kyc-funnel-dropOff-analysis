-- ...

USE kyc_funnel;


-- PART 2 : VALIDATION (run after loading)

SELECT COUNT(*) AS session_rows FROM fact_user_sessions;
SELECT COUNT(*) AS event_rows   FROM fact_events;
SELECT COUNT(*) AS orphan_events
FROM fact_events e
LEFT JOIN fact_user_sessions s ON s.session_id = e.session_id
WHERE s.session_id IS NULL;


---


-- PART 3 : ANALYSIS QUERIES


-- Q1. FUNNEL COUNTS: how many sessions REACHED each step (Volume Velocity)

SELECT stage,
       COUNT(DISTINCT session_id) AS sessions_reached
FROM fact_events
GROUP BY stage
ORDER BY FIELD(stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign');


-- Q2. STAGE-WISE DROP-OFF % : reached vs abandoned AT that step

SELECT stage,
       COUNT(DISTINCT session_id)                                   AS sessions_reached,
       COUNT(DISTINCT CASE WHEN drop_off_flag = 1 THEN session_id END) AS sessions_dropped,
       ROUND(100 * COUNT(DISTINCT CASE WHEN drop_off_flag = 1 THEN session_id END)
                 / COUNT(DISTINCT session_id), 2)                   AS dropoff_pct
FROM fact_events
GROUP BY stage
ORDER BY FIELD(stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign');


-- Q3. FRICTION DENSITY per step: avg retries + error count per session

SELECT stage,
       ROUND(AVG(retry_count), 3)                         AS avg_retry_count,
       SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END) AS total_errors,
       ROUND(SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END)
             / COUNT(DISTINCT session_id), 3)             AS errors_per_session
FROM fact_events
GROUP BY stage
ORDER BY FIELD(stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign');


-- Q4. TIME DWELL per step: average seconds per attempt

SELECT stage,
       ROUND(AVG(time_on_step), 1) AS avg_seconds_per_attempt
FROM fact_events
GROUP BY stage
ORDER BY FIELD(stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign');


-- Q5. DEVICE-TIER COHORT: abandonment rate by device tier

SELECT device_tier,
       COUNT(*)                                  AS sessions,
       SUM(has_abandoned)                        AS abandoned,
       ROUND(100 * AVG(has_abandoned), 2)        AS abandonment_pct
FROM fact_user_sessions
GROUP BY device_tier
ORDER BY abandonment_pct DESC;


-- Q6. DEVICE TIER x STEP: failure rate on each step per tier (proves the camera-step gap)

SELECT device_type,
       stage,
       COUNT(*)                                                       AS attempts,
       ROUND(100 * AVG(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END), 2) AS fail_pct
FROM fact_events
GROUP BY device_type, stage
ORDER BY device_type, FIELD(stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign');


-- Q7. ERROR-IMPACT MAPPING: abandonment rate for sessions that hit each error code

SELECT e.error_type,
       COUNT(DISTINCT e.session_id)                         AS sessions_with_error,
       COUNT(DISTINCT CASE WHEN s.has_abandoned = 1 THEN e.session_id END) AS abandoned_sessions,
       ROUND(100 * COUNT(DISTINCT CASE WHEN s.has_abandoned = 1 THEN e.session_id END)
                 / COUNT(DISTINCT e.session_id), 2)         AS abandonment_pct
FROM fact_events e
JOIN fact_user_sessions s ON s.session_id = e.session_id
WHERE e.error_type IS NOT NULL
GROUP BY e.error_type
ORDER BY abandonment_pct DESC;


-- Q8. TIME-TO-ABANDON COHORTS: total time spent on the step where the user quit

WITH step_time AS (
    SELECT session_id, stage, SUM(time_on_step) AS step_seconds
    FROM fact_events
    GROUP BY session_id, stage
),
quit_points AS (
    SELECT DISTINCT session_id, stage
    FROM fact_events
    WHERE drop_off_flag = 1
)
SELECT q.stage,
       CASE WHEN t.step_seconds < 5  THEN '1_no_intent_<5s'
            WHEN t.step_seconds <= 60 THEN '2_mid_5_to_60s'
            ELSE '3_blocker_60s+' END AS abandon_cohort,
       COUNT(*) AS sessions
FROM quit_points q
JOIN step_time t ON t.session_id = q.session_id AND t.stage = q.stage
GROUP BY q.stage, abandon_cohort
ORDER BY FIELD(q.stage,'registration','phone_otp','doc_upload','liveness_check','consent_sign'), abandon_cohort;


-- Q9. VENDOR COST BLEED: money spent on sessions that never converted (Pain Point 2)

SELECT has_abandoned,
       COUNT(*)                                AS sessions,
       ROUND(SUM(total_vendor_cost), 2)        AS total_vendor_cost_usd,
       ROUND(AVG(total_vendor_cost), 2)        AS avg_cost_per_session_usd
FROM fact_user_sessions
GROUP BY has_abandoned;


-- Q9b. VENDOR COST BLEED (defensible version): fees paid on attempts that FAILED, by step and device tier

SELECT stage,
       device_type,
       SUM(CASE WHEN error_type IS NOT NULL THEN 1 ELSE 0 END)                AS failed_attempts,
       ROUND(SUM(CASE WHEN error_type IS NOT NULL THEN attempt_cost ELSE 0 END), 2) AS wasted_fees_usd
FROM fact_events
WHERE attempt_cost > 0
GROUP BY stage, device_type
ORDER BY wasted_fees_usd DESC;


-- Q10. DEVICE TIER x DOC TYPE: abandonment rate cross-cut (feeds Power BI slicers)

SELECT device_tier, doc_type,
       COUNT(*) AS sessions,
       ROUND(100 * AVG(has_abandoned), 2) AS abandonment_pct
FROM fact_user_sessions
GROUP BY device_tier, doc_type
ORDER BY abandonment_pct DESC;
