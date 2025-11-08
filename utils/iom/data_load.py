import pandas as pd
from pathlib import Path
from .config import AppConfig

DEF_INPUT = "data/raw/student_performance.csv"

def load_dataframe(cfg: AppConfig, path: str | None = None) -> pd.DataFrame:
    csv_path = Path(path or DEF_INPUT)
    df = pd.read_csv(csv_path)
    return df
