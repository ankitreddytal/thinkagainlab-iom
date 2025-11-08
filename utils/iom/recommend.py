from __future__ import annotations
import json
from dataclasses import dataclass
import pandas as pd
from .config import AppConfig
from .clustering import Clusterer

@dataclass
class Recommendation:
    cluster: int
    next_difficulty: int
    topics: list[str]
    tips: list[str]

class Recommender:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.clusterer = Clusterer(cfg)
        self.schema = self._load_schema()

    def _load_schema(self):
        path = self.cfg.knowledge / "schema.json"
        if path.exists():
            return json.loads(path.read_text())
        return {"topics": {"0": ["foundations"], "1": ["practice"], "2": ["advanced"]}}

    def _difficulty_bounds(self):
        return 0, 2

    def _decide_next_difficulty(self, row: dict, cluster: int) -> int:
        acc = row.get("accuracy", 0.0)
        if acc > 1:
            acc = acc / 100.0
        base = int(row.get("difficulty_level", 1))
        next_diff = base + (1 if acc >= 0.8 else (-1 if acc <= 0.5 else 0))
        lo, hi = self._difficulty_bounds()
        return max(lo, min(hi, next_diff))

    def _pick_topics(self, next_difficulty: int) -> list[str]:
        topics_by_level = self.schema.get("topics", {})
        choices = topics_by_level.get(str(next_difficulty)) or topics_by_level.get(next_difficulty) or []
        if not choices:
            return ["core-practice", "review-mistakes", "targeted-quizzes"]
        return choices[:3]

    def _tips(self, row: dict, cluster: int, next_difficulty: int) -> list[str]:
        ts = []
        if row.get("time_spent", 0) < 30:
            ts.append("Increase focused practice to ≥30 mins per session.")
        if row.get("accuracy", 0) < 0.7:
            ts.append("Review error log; drill weak sub-skills before advancing.")
        if next_difficulty > row.get("difficulty_level", 1):
            ts.append("Advance difficulty gradually; keep streaks of 3 passes.")
        else:
            ts.append("Stabilize fundamentals; use spaced repetition.")
        return ts[:3]

    def recommend_one(self, row: dict):
        df = pd.DataFrame([row])
        cluster = int(self.clusterer.predict(df)[0])
        next_diff = self._decide_next_difficulty(row, cluster)
        topics = self._pick_topics(next_diff)
        return Recommendation(cluster, next_diff, topics, self._tips(row, cluster, next_diff))

    def recommend_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        _ = self.clusterer.predict(df)
        recs = []
        for _, row in df.iterrows():
            r = self.recommend_one(row.to_dict())
            recs.append({
                **row.to_dict(),
                "cluster": r.cluster,
                "next_difficulty": r.next_difficulty,
                "topics": ",".join(r.topics),
                "tips": " | ".join(r.tips),
            })
        return pd.DataFrame(recs)
