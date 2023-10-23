run:
	venv/bin/python -m r2_facial_recognition.client -l -D

test:
	venv/bin/python tests/basic_test.py

clean:
	rm -rf ./build ./dist ./*egg-info

venv:
	python3.6 -m venv venv

install: venv clean
	venv/bin/pip install -r requirements.txt
	venv/bin/python setup.py bdist_wheel
	venv/bin/pip install dist/r2_facial_recognition-*-py3-none-any.whl
