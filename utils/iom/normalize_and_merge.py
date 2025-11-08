#!/usr/bin/env python3
import argparse, re
from pathlib import Path
import pandas as pd
from utils.iom.config import AppConfig

ALIASES = {
  "learner_id": ["learner_id","student_id","user_id","id","sid","uid"],
  "time_spent": ["time_spent","time_spent_min","time","minutes_spent","study_time","total_time","duration_min","minutes","time_minutes"],
  "avg_score": ["avg_score","score","mean_score","average_score","avg_marks","percentage","percent","overall_score"],
  "accuracy": ["accuracy","acc","correct_rate","precision","acc_pct","correct_percentage"],
  "difficulty_level": ["difficulty_level","difficulty","level","diff_level"],
  "completion": ["completion","progress","pct_complete","completion_pct"],
  "mastery": ["mastery","mastery_score","mastery_pct"],
  "topic_progress": ["topic_progress","topic_pct","progress_topic"]
}

def find_col(df, names):
    cols = {re.sub(r'\W+','',c.lower()): c for c in df.columns}
    for n in names:
        key = re.sub(r'\W+','',n.lower())
        if key in cols: return cols[key]
    return None

def normalize_df(df):
    out = {}
    for key, alts in ALIASES.items():
        col = find_col(df, alts)
        if col is not None:
            out[key] = df[col]
    ndf = pd.DataFrame(out)

    if "topic_progress" not in ndf.columns:
        if "completion" in ndf.columns:
            ndf["topic_progress"] = pd.to_numeric(ndf["completion"], errors="coerce")
        elif "mastery" in ndf.columns:
            ndf["topic_progress"] = pd.to_numeric(ndf["mastery"], errors="coerce")
        else:
            ndf["topic_progress"] = 0.0

    if "learner_id" not in ndf.columns:
        ndf["learner_id"] = [f"L{ix+1:010d}" for ix in range(len(ndf))]

    if "difficulty_level" in ndf.columns and ndf["difficulty_level"].dtype == object:
        mapping = {"beginner":0,"intermediate":1,"advanced":2}
        ndf["difficulty_level"] = ndf["difficulty_level"].astype(str).str.lower().map(mapping)

    for c in ["time_spent","avg_score","accuracy","difficulty_level","topic_progress"]:
        if c in ndf.columns:
            ndf[c] = pd.to_numeric(ndf[c], errors="coerce")

    for c, default in [("time_spent",0.0), ("avg_score",0.0), ("accuracy",0.0), ("difficulty_level",1), ("topic_progress",0.0)]:
        if c not in ndf.columns:
            ndf[c] = default

    if ndf["avg_score"].max() > 1.0: ndf["avg_score"] = ndf["avg_score"]/100.0
    if ndf["accuracy"].max() > 1.0: ndf["accuracy"] = ndf["accuracy"]/100.0

    return ndf[["learner_id","time_spent","avg_score","accuracy","difficulty_level","topic_progress"]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="data/processed/iom_task2_input.csv")
    args = ap.parse_args()
    _ = AppConfig.load()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.csv, low_memory=False)
    ndf = normalize_df(df).fillna(0)
    ndf.to_csv(args.out, index=False)
    print(args.out)
if __name__ == "__main__":
    main()
