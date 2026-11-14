"""Load one daily batch file into RAW.AUTO_INSURANCE_BATCHES (PUT + COPY INTO).

Idempotent by default: Snowflake remembers loaded files, so re-running a batch loads 0 files.
Use force=True only for deliberate reloads (for example the poison-batch demo).
"""
from common import BATCH_DIR, get_connection


def load_batch(batch_date: str, force: bool = False, conn=None) -> dict:
    path = BATCH_DIR / f"auto_insurance_{batch_date}.csv"
    if not path.exists():
        raise FileNotFoundError(f"No batch file for {batch_date}: {path}")

    own_conn = conn is None
    conn = conn or get_connection()
    try:
        cur = conn.cursor()
        overwrite = "TRUE" if force else "FALSE"
        cur.execute(f"PUT 'file://{path}' @BATCH_STAGE AUTO_COMPRESS=TRUE OVERWRITE={overwrite}")

        force_clause = "FORCE = TRUE" if force else ""
        cur.execute(
            f"""
            COPY INTO AUTO_INSURANCE_BATCHES
            FROM @BATCH_STAGE
            PATTERN = '.*auto_insurance_{batch_date}.csv.gz'
            FILE_FORMAT = (FORMAT_NAME = BATCH_CSV_FF)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
            ON_ERROR = 'ABORT_STATEMENT'
            {force_clause}
            """
        )
        copy_rows = cur.fetchall()
        loaded = [r for r in copy_rows if len(r) > 3 and r[1] == "LOADED"]

        cur.execute(
            "SELECT COUNT(*) FROM AUTO_INSURANCE_BATCHES WHERE BATCH_DATE = %s", (batch_date,)
        )
        rows_in_table = cur.fetchone()[0]

        return {
            "batch_date": batch_date,
            "files_loaded": len(loaded),
            "rows_loaded": int(sum(r[3] for r in loaded)),
            "rows_in_table_for_batch": int(rows_in_table),
        }
    finally:
        if own_conn:
            conn.close()


if __name__ == "__main__":
    import sys

    print(load_batch(sys.argv[1]))