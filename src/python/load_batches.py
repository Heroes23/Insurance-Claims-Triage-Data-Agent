import os
from pathlib import Path
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
BATCH_DIR = ROOT/"data"/"batches"

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"), 
    password=os.getenv("SNOWFLAKE_PASSWORD"), 
    role=os.getenv("SNOWFLAKE_ROLE"), 
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

try:
    snow = conn.cursor()
    snow.execute(f"PUT file://{BATCH_DIR}/auto_insurance_*.csv @BATCH_STAGE AUTO_COMPRESS=TRUE")
    snow.execute("LIST @BATCH_STAGE")
    print(len(snow.fetchall()))

    snow.execute("""
        COPY INTO AUTO_INSURANCE_BATCHES
        FROM @BATCH_STAGE
        FILE_FORMAT = (FORMAT_NAME = BATCH_CSV_FF)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        ON_ERROR = 'ABORT_STATEMENT'
    """)
    print(len(snow.fetchall()))

    snow.execute("SELECT COUNT(*), COUNT(DISTINCT BATCH_DATE) FROM AUTO_INSURANCE_BATCHES")
    print(snow.fetchone())
finally:
    conn.close()