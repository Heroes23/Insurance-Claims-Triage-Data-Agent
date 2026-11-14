"""Inject a deliberately bad batch so dbt tests fail and the triage agent has work to do.

    python src/python/poison_batch.py --scenario duplicate
    cd dbt && dbt test            # tests fail
    python src/python/triage_agent.py

    python src/python/poison_batch.py --clean     # remove the bad batch again
"""
import argparse

import pandas as pd

from common import BATCH_DIR, get_connection
from ingest import load_batch

POISON_DATE = "2026-03-01"
POISON_FILE = BATCH_DIR / f"auto_insurance_{POISON_DATE}.csv"

SCENARIOS = {
    "duplicate": "Two rows share one CUSTOMER id (unique test fails)",
    "bad_category": "COVERAGE = 'Platinum' (accepted_values test fails)",
    "null_state": "STATE is empty (not_null test fails)",
    "bad_date": "EFFECTIVE_TO_DATE = '13/45/2011' (unparseable, not_null test fails)",
    "negative_premium": "MONTHLY_PREMIUM_AUTO = -50 (assert_premium_positive fails)",
}


def build_poison_file(scenario: str) -> pd.DataFrame:
    """Take 25 real rows from the first batch, give them fresh ids, and inject one problem."""
    df = pd.read_csv(BATCH_DIR / "auto_insurance_2026-01-01.csv", dtype=str, keep_default_na=False)
    df = df.head(25).copy()
    df["BATCH_DATE"] = POISON_DATE
    df["CUSTOMER"] = [f"PZ{i:05d}" for i in range(len(df))]

    if scenario == "duplicate":
        df.loc[1, "CUSTOMER"] = df.loc[0, "CUSTOMER"]
    elif scenario == "bad_category":
        df.loc[0, "COVERAGE"] = "Platinum"
    elif scenario == "null_state":
        df.loc[0, "STATE"] = ""
    elif scenario == "bad_date":
        df.loc[0, "EFFECTIVE_TO_DATE"] = "13/45/2011"
    elif scenario == "negative_premium":
        df.loc[0, "MONTHLY_PREMIUM_AUTO"] = "-50"
    else:
        raise ValueError(f"Unknown scenario {scenario!r}")

    df.to_csv(POISON_FILE, index=False)
    return df


def clean() -> None:
    """Remove the poison rows, the staged file and the local file."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM AUTO_INSURANCE_BATCHES WHERE BATCH_DATE = %s", (POISON_DATE,))
        cur.execute(f"REMOVE @BATCH_STAGE PATTERN = '.*auto_insurance_{POISON_DATE}.csv.gz'")
    finally:
        conn.close()
    POISON_FILE.unlink(missing_ok=True)
    print(f"Removed poison batch {POISON_DATE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--scenario", choices=SCENARIOS, help="; ".join(f"{k}: {v}" for k, v in SCENARIOS.items()))
    parser.add_argument("--clean", action="store_true", help="Remove the poison batch")
    args = parser.parse_args()

    if args.clean:
        clean()
        return
    if not args.scenario:
        parser.error("Provide --scenario or --clean")

    clean()  # start from a known state
    build_poison_file(args.scenario)
    print(load_batch(POISON_DATE, force=True))
    print(f"Poison scenario '{args.scenario}' loaded. Now run: cd dbt && dbt test")


if __name__ == "__main__":
    main()