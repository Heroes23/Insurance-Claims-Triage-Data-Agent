-- Landing table for daily batches. Run as TRANSFORMER.
-- Everything is VARCHAR on purpose: RAW stays loose, dbt staging does casting and validation.
USE ROLE TRANSFORMER;
USE WAREHOUSE DE_WH;
USE SCHEMA INSURANCE_DB.RAW;

CREATE TABLE IF NOT EXISTS AUTO_INSURANCE_BATCHES (
    CUSTOMER                       VARCHAR,
    STATE                          VARCHAR,
    CUSTOMER_LIFETIME_VALUE        VARCHAR,
    RESPONSE                       VARCHAR,
    COVERAGE                       VARCHAR,
    EDUCATION                      VARCHAR,
    EFFECTIVE_TO_DATE              VARCHAR,   -- raw text, mixed M/D/YY and M/D/YYYY
    EMPLOYMENT_STATUS              VARCHAR,
    GENDER                         VARCHAR,
    INCOME                         VARCHAR,
    LOCATION_CODE                  VARCHAR,
    MARITAL_STATUS                 VARCHAR,
    MONTHLY_PREMIUM_AUTO           VARCHAR,
    MONTHS_SINCE_LAST_CLAIM        VARCHAR,
    MONTHS_SINCE_POLICY_INCEPTION  VARCHAR,
    NUMBER_OF_OPEN_COMPLAINTS      VARCHAR,
    NUMBER_OF_POLICIES             VARCHAR,
    POLICY_TYPE                    VARCHAR,
    POLICY                         VARCHAR,
    RENEW_OFFER_TYPE               VARCHAR,
    SALES_CHANNEL                  VARCHAR,
    TOTAL_CLAIM_AMOUNT             VARCHAR,
    VEHICLE_CLASS                  VARCHAR,
    VEHICLE_SIZE                   VARCHAR,
    BATCH_DATE                     VARCHAR,   -- synthetic batch key, YYYY-MM-DD
    LOADED_AT                      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE FILE FORMAT IF NOT EXISTS BATCH_CSV_FF
    TYPE = CSV
    PARSE_HEADER = TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL');

CREATE STAGE IF NOT EXISTS BATCH_STAGE FILE_FORMAT = BATCH_CSV_FF;

-- Checks
DESC TABLE AUTO_INSURANCE_BATCHES;
SHOW STAGES LIKE 'BATCH_STAGE';