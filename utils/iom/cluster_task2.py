#!/usr/bin/env python3
import argparse, json
from pathlib import Path
import pandas as pd, numpy as np, joblib
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from utils.iom.config import AppConfig
from utils.iom.features import FeatureBuilder
from pymongo import MongoClient

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--n_clusters", type=int, default=3)
    ap.add_argument("--mongo", default="mongodb://127.0.0.1:27017")
    ap.add_argument("--db", default="iom")
    ap.add_argument("--collection", default="learners")
    ap.add_argument("--no_mongo", action="store_true")
    args=ap.parse_args()

    cfg=AppConfig.load()
    df=pd.read_csv(args.csv)
    fb=FeatureBuilder(cfg)
    X=fb.build(df[cfg.numeric+cfg.categorical], fit=True)

    km=KMeans(n_clusters=cfg.n_clusters, random_state=cfg.random_state).fit(X)
    gmm=GaussianMixture(n_components=cfg.n_clusters, random_state=cfg.random_state).fit(X)

    (cfg.artifacts).mkdir(parents=True, exist_ok=True)
    joblib.dump(km, cfg.artifacts/"kmeans.joblib")
    joblib.dump(gmm, cfg.artifacts/"gmm.joblib")

    df_out=df.copy()
    df_out["cluster_kmeans"]=km.predict(X)
    df_out["cluster_gmm"]=gmm.predict(X)
    df_out["gmm_confidence"]=gmm.predict_proba(X).max(axis=1)

    (cfg.reports).mkdir(parents=True, exist_ok=True)
    out_csv=cfg.reports/"learner_clusters.csv"
    df_out.to_csv(out_csv, index=False)

    if not args.no_mongo:
        try:
            coll=MongoClient(args.mongo)[args.db][args.collection]
            docs=[]
            for _,r in df_out.iterrows():
                d={
                    "learner_id": str(r.get("learner_id","")),
                    "time_spent": float(r.get("time_spent",0)),
                    "avg_score": float(r.get("avg_score",0)),
                    "accuracy": float(r.get("accuracy",0)),
                    "difficulty_level": int(r.get("difficulty_level",1)),
                    "topic_progress": float(r.get("topic_progress",0)),
                    "cluster_kmeans": int(r["cluster_kmeans"]),
                    "cluster_gmm": int(r["cluster_gmm"]),
                    "gmm_confidence": float(r["gmm_confidence"])
                }
                docs.append({"updateOne":{"filter":{"learner_id":d["learner_id"]},"update":{"$set":d},"upsert":True}})
                if len(docs)>=5000:
                    coll.bulk_write(docs, ordered=False); docs=[]
            if docs: coll.bulk_write(docs, ordered=False)
        except Exception as e:
            pass

    summary={
      "csv": args.csv,
      "report_csv": str(out_csv),
      "artifacts": {
        "preprocess": str(cfg.artifacts/"preprocess.joblib"),
        "kmeans": str(cfg.artifacts/"kmeans.joblib"),
        "gmm": str(cfg.artifacts/"gmm.joblib")
      }
    }
    (cfg.reports/"clustering_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary, indent=2))
if __name__=="__main__":
    main()
