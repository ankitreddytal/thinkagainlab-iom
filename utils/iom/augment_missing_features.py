#!/usr/bin/env python3
import argparse, numpy as np, pandas as pd
from pathlib import Path

def synth_time_spent(df):
    rng = np.random.default_rng(42)
    acc = pd.to_numeric(df.get("accuracy", 0), errors="coerce").fillna(0).astype(float)
    if acc.max() > 1: acc = acc/100.0
    avg = pd.to_numeric(df.get("avg_score", 0), errors="coerce").fillna(0).astype(float)
    if avg.max() > 1: avg = avg/100.0
    diff = pd.to_numeric(df.get("difficulty_level", 1), errors="coerce").fillna(1).clip(0,2).astype(float)
    base = 25 + (1-acc)*50 + (2*diff+5)
    noise = rng.normal(0, 8, size=len(df))
    tmin = np.maximum(5, base + noise)
    return np.round(tmin, 1)

def synth_topic_progress(df):
    acc = pd.to_numeric(df.get("accuracy", 0), errors="coerce").fillna(0).astype(float)
    if acc.max() > 1: acc = acc/100.0
    avg = pd.to_numeric(df.get("avg_score", 0), errors="coerce").fillna(0).astype(float)
    if avg.max() > 1: avg = avg/100.0
    tp = 0.6*avg + 0.4*acc
    return tp.clip(0,1).round(4)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.in_csv, low_memory=False)
    out = df.copy()
    if "time_spent" not in out.columns or (pd.to_numeric(out.get("time_spent", 0), errors="coerce").fillna(0)==0).all():
        out["time_spent"] = synth_time_spent(out)
    if "topic_progress" not in out.columns or (pd.to_numeric(out.get("topic_progress", 0), errors="coerce").fillna(0)==0).all():
        if "completion" in out.columns:
            tp = pd.to_numeric(out["completion"], errors="coerce").fillna(0).astype(float)
            if tp.max()>1: tp = tp/100.0
            out["topic_progress"] = tp.clip(0,1)
        elif "mastery" in out.columns:
            tp = pd.to_numeric(out["mastery"], errors="coerce").fillna(0).astype(float)
            if tp.max()>1: tp = tp/100.0
            out["topic_progress"] = tp.clip(0,1)
        else:
            out["topic_progress"] = synth_topic_progress(out)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_csv, index=False)
    print(args.out_csv)
if __name__ == "__main__":
    main()
