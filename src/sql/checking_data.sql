SELECT MIN(effective_to_date) AS min_date,
       MAX(effective_to_date) AS max_date,
       COUNT_IF(effective_to_date IS NULL) AS unparsed_dates,
       COUNT(*) AS total_rows
FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE;


SELECT 'coverage' AS col, coverage AS val, COUNT(*) AS n
FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE GROUP BY val
UNION ALL
SELECT 'policy_type', policy_type, COUNT(*) FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE GROUP BY policy_type
UNION ALL
SELECT 'response', response, COUNT(*) FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE GROUP BY response
UNION ALL
SELECT 'vehicle_size', vehicle_size, COUNT(*) FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE GROUP BY vehicle_size
UNION ALL
SELECT 'state', state, COUNT(*) FROM INSURANCE_DB.ANALYTICS.STG_AUTO_INSURANCE GROUP BY state
ORDER BY col, val;