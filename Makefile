init:
ifeq ($(OS),Windows_NT)
	python -m venv venv
	.\venv\Scripts\activate
	pip install -r requirements.txt
else
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements.txt
endif

index:
ifeq ($(OS),Windows_NT)
	.\venv\Scripts\activate
	python .\main.py -a 'index'
else
	. venv/bin/activate
	python3 ./main.py -a 'index'
endif

download:
ifeq ($(OS),Windows_NT)
	.\venv\Scripts\activate
	python .\main.py -a 'download'
else
	. venv/bin/activate
	python3 ./main.py -a 'download'
endif

video:
ifeq ($(OS),Windows_NT)
	.\venv\Scripts\activate
	python .\main.py -a 'video'
else
	. venv/bin/activate
	python3 ./main.py -a 'video'
endif