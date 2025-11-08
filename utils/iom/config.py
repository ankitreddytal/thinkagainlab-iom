from dataclasses import dataclass
from pathlib import Path
import yaml
@dataclass
class AppConfig:
    raw: Path
    processed: Path
    knowledge: Path
    artifacts: Path
    reports: Path
    n_clusters: int
    random_state: int
    numeric: list
    categorical: list
    difficulty_map: dict
    @staticmethod
    def load(path: str = "config.yaml") -> "AppConfig":
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        p = cfg["paths"]; t = cfg["training"]["kmeans"]; feats = cfg["features"]
        return AppConfig(
            raw=Path(p["raw"]), processed=Path(p["processed"]), knowledge=Path(p["knowledge"]),
            artifacts=Path(p["artifacts"]), reports=Path(p["reports"]),
            n_clusters=t["n_clusters"], random_state=t["random_state"],
            numeric=feats["numeric"], categorical=feats["categorical"], difficulty_map=feats["difficulty_map"]
        )
