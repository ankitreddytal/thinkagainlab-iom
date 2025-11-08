#!/usr/bin/env python3
import argparse, json, pandas as pd, numpy as np, joblib, os
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.exceptions import NotFittedError
from utils.iom.config import AppConfig
from utils.iom.features import FeatureBuilder

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--sample", type=int, default=100000)
    args = ap.parse_args()

    cfg = AppConfig.load()
    df = pd.read_csv(args.csv)
    if len(df) > args.sample:
        df = df.sample(args.sample, random_state=cfg.random_state)

    fb = FeatureBuilder(cfg)

    try:
        X = fb.build(df[cfg.numeric + cfg.categorical], fit=False)
    except (FileNotFoundError, NotFittedError, AttributeError):
        X = fb.build(df[cfg.numeric + cfg.categorical], fit=True)

    Xd = X.toarray() if hasattr(X, "toarray") else X
    km = joblib.load(cfg.artifacts / "kmeans.joblib")

    labels = km.predict(Xd)
    metrics = {
        "sample_size": int(len(df)),
        "silhouette": float(silhouette_score(Xd, labels)),
        "davies_bouldin": float(davies_bouldin_score(Xd, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(Xd, labels)),
        "inertia": float(km.inertia_) if hasattr(km, "inertia_") else None,
        "n_clusters": int(km.n_clusters),
        "preprocess_exists": os.path.exists(cfg.artifacts / "preprocess.joblib"),
    }

    summ_path = cfg.reports / "clustering_summary.json"
    try:
        base = json.loads(summ_path.read_text())
    except Exception:
        base = {}
    base["quality_metrics"] = metrics
    summ_path.write_text(json.dumps(base, indent=2))
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
