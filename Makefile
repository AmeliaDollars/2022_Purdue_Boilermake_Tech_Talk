init:
	python -m venv venv
	.\venv\Scripts\activate
	pip install -r ./requirements.txt
run:
	.\venv\Scripts\activate
	python .\main.py