#!/usr/bin/env python3
import argparse, json, random
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from pymongo import MongoClient
import joblib
from utils.iom.config import AppConfig
from utils.iom.features import FeatureBuilder

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--n_clusters", type=int, default=3)
    ap.add_argument("--chunksize", type=int, default=200000)
    ap.add_argument("--sample_for_gmm", type=int, default=300000)
    ap.add_argument("--mongo", default="mongodb://127.0.0.1:27017")
    ap.add_argument("--db", default="iom")
    ap.add_argument("--collection", default="learners")
    args=ap.parse_args()
    cfg=AppConfig.load()
    fb=FeatureBuilder(cfg)
    client=MongoClient(args.mongo); coll=client[args.db][args.collection]
    mbk=MiniBatchKMeans(n_clusters=args.n_clusters, random_state=cfg.random_state, batch_size=4096)
    sampler=[]; total=0
    first=True
    for chunk in pd.read_csv(args.csv, chunksize=args.chunksize, low_memory=False):
        X=fb.build(chunk[[c for c in set(cfg.numeric+cfg.categorical) if c in chunk.columns]], fit=first); first=False
        X_arr = X.toarray() if hasattr(X,"toarray") else X
        mbk.partial_fit(X_arr)
        for row in X_arr:
            total+=1
            if len(sampler)<args.sample_for_gmm: sampler.append(row)
            else:
                j=random.randint(0,total-1)
                if j<args.sample_for_gmm: sampler[j]=row
    Path(cfg.artifacts).mkdir(parents=True, exist_ok=True)
    joblib.dump(mbk, cfg.artifacts/"kmeans_minibatch.joblib")
    smp=np.asarray(sampler,dtype=float)
    gmm=GaussianMixture(n_components=args.n_clusters, random_state=cfg.random_state).fit(smp)
    joblib.dump(gmm, cfg.artifacts/"gmm.joblib")
    out_csv=cfg.reports/"learner_clusters.csv"; out_csv.parent.mkdir(parents=True, exist_ok=True)
    wrote=False; buf=[]
    for chunk in pd.read_csv(args.csv, chunksize=args.chunksize, low_memory=False):
        X=fb.build(chunk[[c for c in set(cfg.numeric+cfg.categorical) if c in chunk.columns]], fit=False)
        X_arr = X.toarray() if hasattr(X,"toarray") else X
        k=mbk.predict(X_arr); g=gmm.predict(X_arr); p=gmm.predict_proba(X_arr).max(axis=1)
        chunk=chunk.copy()
        chunk["cluster_kmeans"]=k; chunk["cluster_gmm"]=g; chunk["gmm_confidence"]=p
        wanted=["learner_id","time_spent","avg_score","accuracy","difficulty_level","topic_progress","cluster_kmeans","cluster_gmm","gmm_confidence"]
        present=[c for c in wanted if c in chunk.columns]
        if "learner_id" not in present:
            chunk["learner_id"]=[f"L{ix+1:010d}" for ix in range(len(chunk))]
            present=["learner_id"]+present
        chunk[present].to_csv(out_csv, mode="a", index=False, header=(not wrote)); wrote=True
        keep=["learner_id","accuracy","time_spent","difficulty_level","topic_progress"]
        if "avg_score" in chunk.columns: keep.append("avg_score")
        for _,r in chunk.iterrows():
            d={k:(float(r[k]) if k in chunk.columns and pd.notna(r[k]) else None) for k in keep if k in chunk.columns}
            d["learner_id"]=str(r["learner_id"]); d["cluster_kmeans"]=int(r["cluster_kmeans"]); d["cluster_gmm"]=int(r["cluster_gmm"]); d["gmm_confidence"]=float(r["gmm_confidence"])
            buf.append(d)
            if len(buf)>=5000:
                coll.bulk_write([{"updateOne":{"filter":{"learner_id":x["learner_id"]},"update":{"$set":x},"upsert":True}} for x in buf], ordered=False); buf=[]
    if buf:
        coll.bulk_write([{"updateOne":{"filter":{"learner_id":x["learner_id"]},"update":{"$set":x},"upsert":True}} for x in buf], ordered=False)
    summary={"csv":args.csv,"n_clusters":args.n_clusters,"report_csv":str(out_csv),
             "artifacts":{"kmeans_minibatch":str(cfg.artifacts/'kmeans_minibatch.joblib'),
                          "gmm":str(cfg.artifacts/'gmm.joblib'),
                          "preprocess":str(cfg.artifacts/'preprocess.joblib'),
                          "feature_spec":str(cfg.artifacts/'feature_spec.json')}}
    (cfg.reports/"clustering_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    main()
