import pandas as pd, numpy as np, joblib, os
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
ART = Path(os.getenv("ARTIFACTS_DIR","models/intel_artifacts"))
ART.mkdir(parents=True, exist_ok=True)
DATA = Path("data/cleaned/learner_events.parquet")
df = pd.read_parquet(DATA)
feat = df.groupby('learner_id').agg(accuracy_mean=('correct','mean'),time_spent_mean=('time_spent_sec','mean'),difficulty_mean=('difficulty','mean')).fillna(0.0)
X = feat[['accuracy_mean','time_spent_mean','difficulty_mean']].values
kmeans = KMeans(n_clusters=5, n_init='auto', random_state=42).fit(X)
gmm = GaussianMixture(n_components=5, random_state=42).fit(X)
joblib.dump(kmeans, ART/'clustering.kmeans.joblib')
joblib.dump(gmm, ART/'clustering.gmm.joblib')
print("ok")
