#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    mf = out/"master_full.csv"; mc = out/"master_core.csv"
    if not mf.exists() or not mc.exists():
        raise SystemExit("Outputs missing. Run iom_build.py first.")
    df_full = pd.read_csv(mf, nrows=200000, low_memory=False)
    df_core = pd.read_csv(mc, nrows=200000, low_memory=False)
    issues = []
    if df_core.isna().any().any(): issues.append("core_has_nans")
    if df_core.duplicated().any(): issues.append("core_has_duplicates")
    print(json.dumps({
        "sample_rows_full": int(len(df_full)),
        "sample_cols_full": int(df_full.shape[1]),
        "sample_rows_core": int(len(df_core)),
        "sample_cols_core": int(df_core.shape[1]),
        "issues": issues
    }, indent=2))

if __name__ == "__main__":
    main()
