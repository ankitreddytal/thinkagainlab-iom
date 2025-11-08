#!/usr/bin/env python3
import argparse, pandas as pd
from pymongo import MongoClient, UpdateOne

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--mongo", default="mongodb://127.0.0.1:27017")
    ap.add_argument("--db", default="iom")
    ap.add_argument("--collection", default="learners")
    ap.add_argument("--chunksize", type=int, default=200000)
    args = ap.parse_args()

    client = MongoClient(args.mongo)
    coll = client[args.db][args.collection]
    coll.create_index("learner_id", unique=True)

    total = 0
    for chunk in pd.read_csv(args.csv, chunksize=args.chunksize, low_memory=False):
        ops=[]
        for _,r in chunk.iterrows():
            d = {
              "learner_id": str(r.get("learner_id","")),
              "time_spent": float(r.get("time_spent",0)),
              "avg_score": float(r.get("avg_score",0)),
              "accuracy": float(r.get("accuracy",0)),
              "difficulty_level": int(r.get("difficulty_level",1)),
              "topic_progress": float(r.get("topic_progress",0)),
              "cluster_kmeans": int(r.get("cluster_kmeans",0)),
              "cluster_gmm": int(r.get("cluster_gmm",0)),
              "gmm_confidence": float(r.get("gmm_confidence",0.0)),
            }
            ops.append(UpdateOne({"learner_id": d["learner_id"]}, {"$set": d}, upsert=True))
        if ops:
            coll.bulk_write(ops, ordered=False)
            total += len(ops)
            print(f"upserted {total}...")
    print("done:", coll.count_documents({}), "docs")
if __name__ == "__main__":
    main()
