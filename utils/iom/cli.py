import argparse
import pandas as pd
from .config import AppConfig
from .data_load import load_dataframe
from .clustering import Clusterer
from .recommend import Recommender

def build_cmd():
    p = argparse.ArgumentParser(prog="iom-cli")
    sub = p.add_subparsers(dest="cmd")
    fit = sub.add_parser("fit")
    fit.add_argument("--csv", type=str, default=None)
    rec = sub.add_parser("recommend")
    rec.add_argument("--time_spent", type=float, required=True)
    rec.add_argument("--avg_score", type=float, required=True)
    rec.add_argument("--accuracy", type=float, required=True)
    rec.add_argument("--difficulty_level", type=int, required=True)
    return p

def main():
    CFG = AppConfig.load()
    args = build_cmd().parse_args()
    if args.cmd == "fit":
        df = load_dataframe(CFG, args.csv)
        Clusterer(CFG).fit(df)
        print("[OK] Model trained & artifacts saved ->", CFG.artifacts)
    elif args.cmd == "recommend":
        row = {
            "time_spent": args.time_spent,
            "avg_score": args.avg_score,
            "accuracy": args.accuracy,
            "difficulty_level": args.difficulty_level,
        }
        rec = Recommender(CFG).recommend_one(row)
        print({
            "cluster": rec.cluster,
            "next_difficulty": rec.next_difficulty,
            "topics": rec.topics,
            "tips": rec.tips,
        })
    else:
        print("Use subcommands: fit | recommend")

if __name__ == "__main__":
    main()
