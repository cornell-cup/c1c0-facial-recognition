run:
	venv/bin/python -m r2_facial_recognition.client -l -D

test:
	sudo venv/bin/python basic_test.py

venv:
	python3.6 -m venv venv

install: venv
	venv/bin/pip install -r requirements.txt
