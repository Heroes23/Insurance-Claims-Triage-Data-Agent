import pandas as pd 
from datetime import date, timedelta 
from pathlib import Path 

ROOT = Path(__file__).resolve().parents[2]

df = pd.read_csv(ROOT / "data" / "AutoInsurance.csv", dtype=str, keep_default_na=False)

print(df.columns.tolist())

# Rename columns 
df = df.rename(columns={"EmploymentStatus": "Employment Status"})
df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]

print(df.columns)


# Add batch date 

N_BATCHES = 59 
START = date(2026, 1, 1) 

df = df.sort_values("CUSTOMER").reset_index(drop=True)
df["BATCH_DATE"] = [(START + timedelta(days=i % N_BATCHES)).isoformat() for i in df.index]

counts = df["BATCH_DATE"].value_counts() 
print(counts.size, counts.min(), counts.max())


# Make into batches 
out_dir = ROOT / "data" / "batches"
out_dir.mkdir(parents=True, exist_ok=True)

for batch_date, batch_df in df.groupby("BATCH_DATE"):
    batch_df.to_csv(out_dir / f"auto_insurance_{batch_date}.csv", index=False)

print(f"Wrote {df['BATCH_DATE'].nunique()} files to {out_dir}")