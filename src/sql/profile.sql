USE ROLE TRANSFORMER;
USE WAREHOUSE DE_WH;
USE SCHEMA INSURANCE_DB.RAW;

-- 1. How many rows?
SELECT COUNT(*) AS row_count FROM AUTO_INSURANCE;

-- 2. Is each CUSTOMER unique? (both numbers should match)
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT CUSTOMER) AS distinct_customers
FROM AUTO_INSURANCE;

-- 3. What dates does the data cover?
SELECT MIN(EFFECTIVE_TO_DATE) AS earliest,
       MAX(EFFECTIVE_TO_DATE) AS latest,
       COUNT(DISTINCT EFFECTIVE_TO_DATE) AS distinct_days
FROM AUTO_INSURANCE;

-- 0011-01-13 isn’t a valid date for this data, and the latest value (2011-12-02) is suspicious. 
-- This dataset should cover about two months of early 2011, but the values span a whole year.