from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
from utils.iom.config import AppConfig
from utils.iom.recommend import Recommender

app = FastAPI(title="IOM Learning Recommender")
CFG = AppConfig.load()
REC = Recommender(CFG)

class InputRow(BaseModel):
    time_spent: float = Field(..., ge=0)
    avg_score: float = Field(..., ge=0)
    accuracy: float = Field(..., ge=0)
    difficulty_level: int = Field(..., ge=0, le=10)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/clusters")
async def clusters():
    return {"n_clusters": CFG.n_clusters}

@app.post("/recommend")
async def recommend(row: InputRow):
    r = REC.recommend_one(row.model_dump())
    return {
        "cluster": r.cluster,
        "next_difficulty": r.next_difficulty,
        "topics": r.topics,
        "tips": r.tips,
    }

@app.post("/batch_recommend")
async def batch(csv_path: str):
    df = pd.read_csv(csv_path)
    out = REC.recommend_batch(df)
    save = CFG.reports / "batch_recommendations.csv"
    save.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(save, index=False)
    return {"rows": len(out), "saved": str(save)}
