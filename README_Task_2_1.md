# Task 2.1 – Learner Clustering and Profiling

### Objective
The goal of this task is to segment learners based on their behavior and performance using K-Means and Gaussian Mixture Models (GMM). The clustered results are stored in MongoDB, along with summary reports and reproducible artifacts.

---

## Folder Structure
```
IOM/
├── config.yaml
├── utils/iom/
│   ├── normalize_and_merge.py
│   ├── cluster_task2.py
│   ├── mongo_upsert_from_csv.py
│   ├── features.py
│   ├── quality_metrics.py
├── data/
│   ├── raw/
│   ├── processed/iom_task2_input_aug.csv
│   └── knowledge/
│       ├── schema.json
│       └── learning_graph_design.md
├── models/
│   ├── preprocess.joblib
│   ├── kmeans.joblib
│   └── gmm.joblib
├── reports/
│   ├── learner_clusters.csv(.gz)
│   ├── cluster_profiles.csv
│   ├── clustering_summary.json
│   └── task_2_1_report.md
└── IOM_Task_2_1_Submission.tgz
```

---

## Environment Setup
```bash
cd ~/Documents/IOM
python3 -m venv iom_env
source iom_env/bin/activate
pip install -r requirements.txt  # pandas, scikit-learn, joblib, pymongo, tabulate, pyyaml
export PYTHONPATH="$(pwd)"
```

---

## Steps to Reproduce

### 1. Data Preparation
```bash
python3 -m utils.iom.normalize_and_merge   --csv data_local_backup/iom_datasets/final_dataset.csv   --out data/processed/iom_task2_input_aug.csv
```
This step normalizes the dataset, ensures proper schema alignment, and scales the numeric features.

---

### 2. Clustering
```bash
python3 -m utils.iom.cluster_task2   --csv data/processed/iom_task2_input_aug.csv   --n_clusters 3   --mongo "mongodb://127.0.0.1:27017"   --db iom   --collection learners   --no_mongo
```
This script performs K-Means and GMM clustering and saves model artifacts.

---

### 3. Cluster Profiling
```bash
python3 - <<'PY'
import pandas as pd, pathlib
df = pd.read_csv("reports/learner_clusters.csv")
prof = df.groupby("cluster_kmeans")[["time_spent","avg_score","accuracy","topic_progress"]].mean().round(4)
prof["count"] = df.groupby("cluster_kmeans").size()
prof.reset_index().rename(columns={"cluster_kmeans":"cluster"}).to_csv("reports/cluster_profiles.csv", index=False)
PY
```
Generates a summary file showing average metrics per cluster.

---

### 4. Quality Metrics
```bash
python3 utils/iom/quality_metrics.py   --csv data/processed/iom_task2_input_aug.csv   --sample 100000
```
Calculates silhouette score, Davies–Bouldin index, Calinski–Harabasz score, and inertia.

---

### 5. MongoDB Integration
Ensure MongoDB is running:
```bash
/opt/homebrew/opt/mongodb-community/bin/mongod --dbpath "$HOME/.local/share/mongodb/data" --bind_ip 127.0.0.1 --port 27017
```

Then run:
```bash
python3 utils/iom/mongo_upsert_from_csv.py   --csv reports/learner_clusters.csv   --mongo "mongodb://127.0.0.1:27017"   --db iom   --collection learners
```

Check inserted documents:
```bash
/opt/homebrew/bin/mongosh --eval '
db.getSiblingDB("iom").learners.aggregate([
  {$match:{time_spent:{$gt:0}, topic_progress:{$gt:0}}},
  {$limit:5},
  {$project:{_id:0, learner_id:1, time_spent:1, topic_progress:1, cluster_kmeans:1, cluster_gmm:1, gmm_confidence:1}}
]).forEach(printjson)
'
```

---

### 6. Reports and Submission
```bash
python3 - <<'PY'
import json, pandas as pd, pathlib
s=json.loads(pathlib.Path("reports/clustering_summary.json").read_text())
p=pd.read_csv("reports/cluster_profiles.csv")
pathlib.Path("reports/task_2_1_report.md").write_text(
  "# Task 2.1 Report

## Quality Metrics
"+
  json.dumps(s.get("quality_metrics", {}), indent=2)+
  "

## Cluster Profiles
"+p.to_markdown(index=False)
)
PY

gzip -f -k reports/learner_clusters.csv
mkdir -p submission
cp -f reports/task_2_1_report.md reports/cluster_profiles.csv reports/clustering_summary.json submission/
cp -f models/*.joblib submission/
cp -f reports/learner_clusters.csv.gz submission/
tar -czf IOM_Task_2_1_Submission.tgz -C submission .
```
This generates the final submission archive.

---

## Results Summary

| Cluster | Avg. Time Spent | Avg. Score | Accuracy | Topic Progress | Count |
|----------|-----------------|------------|-----------|----------------|--------|
| 0 | 42.15 | 0.7783 | 0.8056 | 0.7892 | 3,062,155 |
| 1 | 64.28 | 0.4565 | 0.4270 | 0.4447 | 2,889,878 |
| 2 | 53.18 | 0.6172 | 0.6168 | 0.6170 | 5,004,449 |

**Quality Metrics**
- Silhouette: 0.3662  
- Davies–Bouldin: 0.8822  
- Calinski–Harabasz: 113,640.93  
- Inertia: 13,375,109.96  
- Sample size: 100,000  
- Number of clusters: 3

---

**Final Status:** Task 2.1 successfully completed with full accuracy and reproducibility.
