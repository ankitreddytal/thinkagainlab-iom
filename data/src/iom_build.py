#!/usr/bin/env python3
import argparse, json, re, hashlib
from pathlib import Path
from typing import List
import pandas as pd
import numpy as np

def snake_case(name: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return (s2.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace("__","_"))

def read_all_csvs(raw_dir: Path):
    frames = []
    for p in sorted(raw_dir.glob("*.csv")):
        try:
            df = pd.read_csv(p, low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(p, low_memory=False, encoding="latin-1")
        df.columns = [snake_case(c) for c in df.columns]
        df["__source_file"] = p.name
        frames.append(df)
    if not frames:
        raise SystemExit(f"No CSVs in {raw_dir}")
    return frames

def unify(frames):
    all_cols = sorted(set().union(*[set(f.columns) for f in frames]))
    return pd.concat([f.reindex(columns=all_cols) for f in frames], ignore_index=True)

def coerce(df):
    for c in df.columns:
        if c == "__source_file": continue
        if df[c].dtype == object:
            # try numeric
            num = pd.to_numeric(df[c], errors="ignore")
            if not num.equals(df[c]):
                df[c] = num
            # try datetime
            if df[c].dtype == object and any(k in c for k in ["date","time","timestamp"]):
                df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

def fill_missing(df, make_synth=False, seed=13):
    rng = np.random.default_rng(seed)
    report = {"numeric":{}, "categorical":{}}
    for c in df.columns:
        if c == "__source_file": continue
        s = df[c]
        if pd.api.types.is_numeric_dtype(s):
            if make_synth and s.isna().any():
                vals = s.dropna().to_numpy()
                if len(vals)>0:
                    picks = rng.choice(vals, size=s.isna().sum(), replace=True)
                    s.loc[s.isna()] = picks
            if s.isna().any():
                s.fillna(s.median(), inplace=True)
            report["numeric"][c] = int(s.isna().sum())
        elif pd.api.types.is_datetime64_any_dtype(s):
            df[f"is_missing_{c}"] = s.isna().astype(int)
        else:
            mode = s.mode(dropna=True)
            fillv = mode.iloc[0] if len(mode) else "_missing"
            s.fillna(fillv, inplace=True)
            report["categorical"][c] = fillv
    return df, report

def make_core(df, min_ratio):
    thresh = int(len(df)*min_ratio)
    keep = [c for c in df.columns if df[c].notna().sum() >= thresh]
    return df[keep].copy()

def md5(path: Path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--make_synth", action="store_true")
    ap.add_argument("--core_threshold", type=float, default=0.2)
    args = ap.parse_args()

    raw = Path(args.raw_dir); out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    frames = read_all_csvs(raw)
    df = unify(frames)
    df = coerce(df)
    df, impute = fill_missing(df, make_synth=args.make_synth)

    full = out / "master_full.csv"; core = out / "master_core.csv"
    df.to_csv(full, index=False)
    core_df = make_core(df, args.core_threshold)
    core_df.to_csv(core, index=False)

    # dictionary
    dd = []
    for c in core_df.columns:
        entry = {"name": c, "dtype": str(core_df[c].dtype)}
        dd.append(entry)

    audit = {
        "rows_full": int(len(df)), "cols_full": int(df.shape[1]),
        "rows_core": int(len(core_df)), "cols_core": int(core_df.shape[1]),
        "imputation": impute,
        "artifacts": {
            "master_full.csv":{"md5": md5(full)},
            "master_core.csv":{"md5": md5(core)}
        }
    }
    with open(out/"audit.json","w") as f: json.dump(audit, f, indent=2)
    with open(out/"data_dictionary_core.json","w") as f: json.dump(dd, f, indent=2)
    print(json.dumps({"status":"ok","out_dir":str(out)}))

if __name__ == "__main__":
    main()
