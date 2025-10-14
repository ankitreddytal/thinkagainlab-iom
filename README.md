# Think Again Lab — IoM (Task 1.1 Starter)

This repo is a ready-to-run scaffold for **Task 1.1 – Environment Setup** on **macOS (Apple Silicon: M1/M2/M3)**.

## 1) macOS prerequisites
```bash
# 1. Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Command Line Tools (if prompted)
xcode-select --install
```

## 2) Python & virtual env (recommended: 3.11)
```bash
brew install python@3.11
python3.11 -m venv iom_env
source iom_env/bin/activate   # <-- zsh default on macOS
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> To leave the venv later: `deactivate`

## 3) MongoDB (choose ONE)
### A) Local (fastest to start)
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0   # start on login
# To stop: brew services stop mongodb-community@7.0
```
Local default URI: `mongodb://localhost:27017`

### B) Atlas (cloud)
Create a free cluster → copy your connection string, e.g.
```
MONGODB_URI="mongodb+srv://<user>:<pass>@cluster0.abcd.mongodb.net/iom"
```

Create a `.env` file at repo root and put:
```
MONGODB_URI="mongodb://localhost:27017"
```

## 4) Run the sample apps
### FastAPI
```bash
# Terminal 1
source iom_env/bin/activate
uvicorn fastapi_app.main:app --reload
# Open http://127.0.0.1:8000  (docs: http://127.0.0.1:8000/docs)
```

### Flask
```bash
# Terminal 2
source iom_env/bin/activate
python flask_app/app.py
# Open http://127.0.0.1:5000
```

## 5) Quick curl tests
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:5000/
```

## 6) Common macOS tips
- If a port is stuck, free it:  
  `lsof -i :8000 | awk 'NR>1 {print $2}' | xargs kill -9`
- If `uvicorn` not found, ensure venv is active (`which python` should point inside `iom_env`).
- If Mongo fails to start, check: `log show --predicate 'process == "mongod"' --last 1h`

## 7) Next steps (Task 1.2/1.3)
- Add your IoM/LBM summary in `docs/`
- Use `notebooks/` for preprocessing and create `data/cleaned_data.csv`

— Ankit Reddy • Think Again Lab (Task 1.1)