.PHONY: run dashboard time
.DEFAULT_GOAL: run

run:
	source .venv/bin/activate && python3 -Xgil=0 ./src/main.py

dashboard:
	source .venv/bin/activate && python3 ./src/dashboard.py

time:
	source .venv/bin/activate && time python3 -Xgil=0 ./src/main.py
