import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()  # reads .env; run from the repo root so it finds the file

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
    snow.execute("SELECT COUNT(*) FROM AUTO_INSURANCE")
    row = snow.fetchone()
    print(row[0])
finally:
    conn.close()