import pandas as pd, numpy as np, random, glob, os
from pathlib import Path
random.seed(42); np.random.seed(42)
root=Path.cwd()
cand=[root/"data_local_backup"/"raw", root/"data_local_backup"/"iom_datasets"]
files=[]
for d in cand:
    if d.exists(): files+=glob.glob(str(d/"*.csv"))
parts=[]
target_total=60000
target_per_file=20000
def pick(df,keys):
    m={c.lower().strip():c for c in df.columns}
    for k in keys:
        if k in m: return m[k]
    for c in df.columns:
        cl=c.lower()
        if any(k in cl for k in keys): return c
    return None
for f in files:
    try:
        df=pd.read_csv(f, nrows=target_per_file, low_memory=False, on_bad_lines='skip')
    except Exception:
        continue
    learner=pick(df,["learner_id","student_id","studentid","userid","user id","id"])
    content=pick(df,["content_id","activity","module_id","resource","assessment_id","course_id","course","vle_id"])
    topic=pick(df,["topic","subject","module","area","course"])
    diff=pick(df,["difficulty","level","grade","g1","g2","g3"])
    tsec=pick(df,["time_spent_sec","duration","time","studytime","spent"])
    corr=pick(df,["correct","is_correct","passed","result","final_result","score","marks"])
    if learner is None: df["_lid"]=[f"L{str(i).zfill(6)}" for i in range(len(df))]; learner="_lid"
    if content is None: df["_cid"]=[f"C{str(i).zfill(6)}" for i in range(len(df))]; content="_cid"
    tp = df[topic].astype(str) if topic else pd.Series(np.random.choice(["arrays","loops","recursion","graphs","trees","dp","ml","ai","math","stats"], size=len(df)))
    if diff is not None:
        x=pd.to_numeric(df[diff], errors="coerce")
        if x.notna().any():
            if x.max()<=1: dv=x.clip(0,1)
            elif x.max()<=20: dv=(x/20).clip(0,1)
            else: dv=(x/x.max()).clip(0,1)
        else:
            dv=pd.Series(np.nan, index=df.index)
    else:
        dv=pd.Series(np.nan, index=df.index)
    dv=dv.fillna(pd.Series(np.random.uniform(0.3,0.9,len(df))))
    if tsec is not None:
        if df[tsec].dtype==object:
            sv=pd.to_timedelta(df[tsec], errors="coerce").dt.total_seconds()
        else:
            sv=pd.to_numeric(df[tsec], errors="coerce")
    else:
        sv=pd.Series(np.nan, index=df.index)
    sv=sv.fillna(pd.Series(np.random.randint(60,1200,len(df)))).clip(lower=1).astype(int)
    if corr is not None:
        c=df[corr]
        if c.dtype==object:
            cl=c.astype(str).str.lower()
            ok=cl.isin(["pass","passed","true","yes","correct","1"]).astype(int)
            bad=cl.isin(["fail","failed","false","no","incorrect","0"]).astype(int)
            y=ok.where(ok==1, 1-bad) if (ok.sum()+bad.sum())>0 else pd.Series(np.nan, index=df.index)
        else:
            cn=pd.to_numeric(c, errors="coerce")
            if cn.notna().any():
                if cn.max()<=1: y=(cn>=0.6).astype(int)
                elif cn.max()<=20: y=(cn>=12).astype(int)
                else: y=(cn>=0.6*cn.max()).astype(int)
            else:
                y=pd.Series(np.nan, index=df.index)
    else:
        y=pd.Series(np.nan, index=df.index)
    y=y.fillna(pd.Series(np.random.choice([0,1], size=len(df)))).astype(int)
    part=pd.DataFrame({
        "learner_id": df[learner].astype(str).str.strip().replace("", "L00000"),
        "content_id": df[content].astype(str).str.strip().replace("", "C00000"),
        "topic": tp.astype(str).str.strip().replace("", "general"),
        "difficulty": dv.astype(float).clip(0,1),
        "time_spent_sec": sv.astype(int),
        "correct": y.clip(0,1).astype(int)
    })
    parts.append(part)
    if sum(len(p) for p in parts)>=target_total: break
mix=pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["learner_id","content_id","topic","difficulty","time_spent_sec","correct"])
need=max(0,60000-len(mix))
if need>0:
    learners=[f"L{str(i).zfill(4)}" for i in range(1,801)]
    contents=[f"C{str(i).zfill(4)}" for i in range(1,301)]
    topics=["arrays","loops","recursion","graphs","trees","dp","ml","ai","math","stats"]
    synth=pd.DataFrame({
        "learner_id": np.random.choice(learners, size=need),
        "content_id": np.random.choice(contents, size=need),
        "topic": np.random.choice(topics, size=need),
        "difficulty": np.random.uniform(0.3,0.9, size=need).round(2),
        "time_spent_sec": np.random.randint(60,1200, size=need),
        "correct": np.random.choice([0,1], size=need)
    })
    mix=pd.concat([mix, synth], ignore_index=True)
Path("data/cleaned").mkdir(parents=True, exist_ok=True)
mix.to_csv("data/cleaned/learner_events.csv", index=False)
mix.to_parquet("data/cleaned/learner_events.parquet", index=False)
print(len(mix))
