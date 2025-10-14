from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="IoM FastAPI — Task 1.1", version="0.1.0")

class HealthResponse(BaseModel):
    status: str
    env: dict

@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(
        status="ok",
        env={
            "MONGODB_URI_present": bool(os.getenv("MONGODB_URI"))
        }
    )