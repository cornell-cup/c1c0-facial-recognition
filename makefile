all:
	sudo venv/bin/python main.py

cache:
	sudo venv/bin/python cache.py

clean:
	sudo rm -rf .cache/ client/__pycache/

install: venv
	venv/bin/pip install -r requirements.txt
	if [ "$(shell uname -s)" == "Darwin" ]; then brew install imagemagick; fi
	if [ "$(shell expr substr $(uname -s) 1 5)" == "Linux" ]; then sudo apt-get install imagemagick; fi

venv:
	sudo rm -rf venv/
	python -m venv/ venv/
