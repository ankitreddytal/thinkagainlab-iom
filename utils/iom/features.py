import json, joblib, pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from utils.iom.config import AppConfig
SPEC_NAME="feature_spec.json"; PIPE_NAME="preprocess.joblib"
class FeatureBuilder:
    def __init__(self, cfg: AppConfig):
        self.cfg=cfg; self.pipe=None
    def _ensure_pipe_loaded(self):
        if self.pipe is None:
            path=self.cfg.artifacts/PIPE_NAME
            if path.exists(): self.pipe=joblib.load(path)
    def build(self, df: pd.DataFrame, fit=True):
        df=df.copy()
        num_cols=[c for c in self.cfg.numeric if c in df.columns]
        cat_cols=[c for c in self.cfg.categorical if c in df.columns]
        if fit or self.pipe is None:
            pre=ColumnTransformer([("num",StandardScaler(),num_cols),("cat",OneHotEncoder(handle_unknown="ignore"),cat_cols)])
            self.pipe=Pipeline([("pre",pre)])
        if fit:
            X=self.pipe.fit_transform(df[num_cols+cat_cols])
            (self.cfg.artifacts/SPEC_NAME).write_text(json.dumps({"numeric":num_cols,"categorical":cat_cols},indent=2))
            (self.cfg.artifacts).mkdir(parents=True, exist_ok=True)
            joblib.dump(self.pipe, self.cfg.artifacts/PIPE_NAME)
        else:
            self._ensure_pipe_loaded()
            X=self.pipe.transform(df[num_cols+cat_cols])
        return X
