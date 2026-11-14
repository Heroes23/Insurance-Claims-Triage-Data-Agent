"""Shared paths and Snowflake connection helper."""
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = ROOT / "dbt"
BATCH_DIR = ROOT / "data" / "batches"
REPORTS_DIR = ROOT / "reports"
PATCHES_DIR = ROOT / "patches"

load_dotenv(ROOT / ".env")


def get_connection(role: str | None = None):
    """Open a Snowflake connection. role=None uses SNOWFLAKE_ROLE (TRANSFORMER)."""
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=role or os.getenv("SNOWFLAKE_ROLE", "TRANSFORMER"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "DE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "INSURANCE_DB"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
    )