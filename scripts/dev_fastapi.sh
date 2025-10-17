#!/bin/zsh
source ./iom_env/bin/activate
uvicorn fastapi_app.main:app --reload --port 8000