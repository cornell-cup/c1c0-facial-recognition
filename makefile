all: install
	sudo venv/bin/python main.py

cache: install
	sudo venv/bin/python cache.py

clean: 
	sudo rm -rf .cache/ client/__pycache/

install: venv
	venv/bin/pip install -r requirements.txt
	sudo apt-get install imagemagick

venv:
	sudo rm -rf venv/
	python3.6 -m venv/ venv/

