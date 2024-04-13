all:
	sudo venv/bin/python main.py

cache:
	sudo venv/bin/python cache.py

clean:
	sudo rm -rf .cache/ client/__pycache__/ __pycache__/

install: venv
	venv/bin/pip install --upgrade pip setuptools wheel
	venv/bin/pip install -r requirements.txt
	if [ "$(shell uname -s)" = "Darwin" ]; then brew install imagemagick; fi
	if [ "$(shell uname -s)" = "Linux" ]; then sudo apt-get install imagemagick; fi

venv:
	if [ "$(shell uname -s)" = "Darwin" ]; then python3.11 -m venv venv/; fi
	if [ "$(shell uname -s)" = "Linux" ]; then python3.6 -m venv venv/; fi
