.PHONY: deps build api report
VENV=iom_env
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

deps:
	$(PIP) install -r requirements.txt

build:
	$(PY) -m utils.iom.cli fit --csv data/raw/student_performance.csv

api:
	uvicorn fastapi_app.recommender_app:app --reload

report:
	@echo "# Task 2.1 Report" > reports/task_2_1_report.md
	@echo "Artifacts saved under models/." >> reports/task_2_1_report.md
