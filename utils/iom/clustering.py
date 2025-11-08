import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from .config import AppConfig
from .features import FeatureBuilder
from pathlib import Path

MODEL_NAME = "kmeans.joblib"
CENTROIDS = "centroids.csv"

class Clusterer:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.model = None
        self.feats = FeatureBuilder(cfg)

    def fit(self, df: pd.DataFrame):
        X = self.feats.build(df, fit=True)
        kmeans = KMeans(n_clusters=self.cfg.n_clusters, random_state=self.cfg.random_state)
        kmeans.fit(X)
        self.model = kmeans
        self._save()
        self._save_centroids()

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        model_path = self.cfg.artifacts / MODEL_NAME
        pipe_path = self.cfg.artifacts / "preprocess.joblib"

        if self.model is None and model_path.exists():
            self.model = joblib.load(model_path)

        # force load fitted pipeline
        self.feats._ensure_pipe_loaded()
        X = self.feats.build(df, fit=False)
        return self.model.predict(X)

    def _save(self):
        out = self.cfg.artifacts / MODEL_NAME
        out.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, out)

    def _save_centroids(self):
        c = self.model.cluster_centers_
        pd.DataFrame(c).to_csv(self.cfg.artifacts / CENTROIDS, index=False)
