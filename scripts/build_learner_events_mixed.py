import pandas as pd, numpy as np, pathlib, re, random, json
from pathlib import Path

random.seed(42); np.random.seed(42)
root = Path.cwd()
cand_dirs = [
    root/"data_local_backup"/"raw",
    root/"data_local_backup"/"iom_datasets"
]
files = []
for d in cand_dirs:
    if d.exists():
        files += list(d.rglob("*.csv"))

def pick_col(df, names):
    for n in names:
        for c in df.columns:
            if c.lower().strip()==n.lower().strip():
                return c
    return None

def norm_num(s):
    try:
        x = pd.to_numeric(s, errors="coerce")
    except:
        x = pd.Series([np.nan]*len(s))
    return x

def parse_duration_to_sec(s):
    if s.dtype==object:
        td = pd.to_timedelta(s, errors="coerce")
        v = td.dt.total_seconds()
    else:
        v = pd.to_numeric(s, errors="coerce")
    if v.notna().mean()<0.2:
        v = pd.Series(np.nan, index=s.index)
    return v

out = []
lid_counter = 1
cid_counter = 1
topics_seed = ["arrays","loops","recursion","graphs","trees","dp","ml","ai","math","stats"]

for f in files:
    try:
        df = pd.read_csv(f, low_memory=False)
    except Exception:
        continue

    learner_col = pick_col(df, ["learner_id","student_id","studentid","user id","userid","id"])
    content_col = pick_col(df, ["content_id","activity","module_id","resource","assessment_id","course","course_id","vle_id"])
    topic_col   = pick_col(df, ["topic","subject","module","area","course"])
    diff_col    = pick_col(df, ["difficulty","level","grade","g1","g2","g3"])
    time_col    = pick_col(df, ["time_spent_sec","duration","time","studytime","spent"])
    corr_col    = pick_col(df, ["correct","is_correct","passed","result","final_result","score","marks"])

    if learner_col is None:
        df["_lid"] = [f"L{str(i).zfill(5)}" for i in range(lid_counter, lid_counter+len(df))]
        learner_col = "_lid"; lid_counter += len(df)

    if content_col is None:
        df["_cid"] = [f"C{str(i).zfill(5)}" for i in range(cid_counter, cid_counter+len(df))]
        content_col = "_cid"; cid_counter += len(df)

    topic = df[topic_col] if topic_col else pd.Series(np.random.choice(topics_seed, size=len(df)))
    diff = None
    if diff_col:
        if diff_col.lower() in ["g1","g2","g3","grade"]:
            g = norm_num(df[diff_col])
            if g.max()<=1.0:
                diff = g.clip(0,1)
            elif g.max()<=20:
                diff = (g/20.0).clip(0,1)
            else:
                diff = (g/g.max()).clip(0,1)
        else:
            d = norm_num(df[diff_col]); diff = (d-d.min())/(d.max()-d.min()) if d.notna().any() else None
    if diff is None or diff.notna().mean()<0.3:
        diff = pd.Series(np.random.uniform(0.3,0.9,len(df)))

    tsec = None
    if time_col:
        tsec = parse_duration_to_sec(df[time_col])
        if tsec.notna().mean()<0.3:
            tsec = None
    if tsec is None:
        tsec = pd.Series(np.random.randint(60,1200,len(df)))

    corr = None
    if corr_col:
        s = df[corr_col]
        if s.dtype==object:
            sp = s.astype(str).str.lower()
            if sp.isin(["pass","passed","true","yes","correct", "1"]).mean()>0.3:
                corr = sp.isin(["pass","passed","true","yes","correct","1"]).astype(int)
            elif sp.isin(["fail","failed","false","no","incorrect","0"]).mean()>0.3:
                corr = (~sp.isin(["fail","failed","false","no","incorrect","0"])).astype(int)
        if corr is None:
            n = norm_num(s)
            if n.notna().any():
                if n.max()<=1.0:
                    corr = (n>=0.6).astype(int)
                elif n.max()<=20:
                    corr = (n>=12).astype(int)
                else:
                    corr = (n>=0.6*n.max()).astype(int)
    if corr is None:
        corr = pd.Series(np.random.choice([0,1], size=len(df)))

    part = pd.DataFrame({
        "learner_id": df[learner_col].astype(str),
        "content_id": df[content_col].astype(str),
        "topic": topic.astype(str),
        "difficulty": diff.astype(float).clip(0,1),
        "time_spent_sec": tsec.astype(float).clip(lower=1).astype(int),
        "correct": corr.astype(int).clip(0,1)
    })

    part = part.sample(min(len(part), 20000), random_state=42)
    out.append(part)

mix = pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["learner_id","content_id","topic","difficulty","time_spent_sec","correct"])

if len(mix)<3000:
    n_add = 3000-len(mix)
    learners = [f"L{str(i).zfill(3)}" for i in range(1,201)]
    contents = [f"C{str(i).zfill(3)}" for i in range(1,101)]
    rows = []
    for _ in range(n_add):
        rows.append([
            random.choice(learners),
            random.choice(contents),
            random.choice(topics_seed),
            round(random.uniform(0.3,0.9),2),
            random.randint(60,1200),
            random.choice([0,1])
        ])
    synth = pd.DataFrame(rows, columns=["learner_id","content_id","topic","difficulty","time_spent_sec","correct"])
    mix = pd.concat([mix, synth], ignore_index=True)

mix["learner_id"] = mix["learner_id"].str.strip().replace("", np.nan).fillna("L00000")
mix["content_id"] = mix["content_id"].str.strip().replace("", np.nan).fillna("C00000")
mix["topic"] = mix["topic"].str.strip().replace("", "general")
mix["difficulty"] = pd.to_numeric(mix["difficulty"], errors="coerce").fillna(0.5).clip(0,1)
mix["time_spent_sec"] = pd.to_numeric(mix["time_spent_sec"], errors="coerce").fillna(300).clip(lower=1).astype(int)
mix["correct"] = pd.to_numeric(mix["correct"], errors="coerce").fillna(0).clip(0,1).astype(int)

Path("data/cleaned").mkdir(parents=True, exist_ok=True)
mix.to_csv("data/cleaned/learner_events.csv", index=False)
mix.to_parquet("data/cleaned/learner_events.parquet", index=False)
print(len(mix))
