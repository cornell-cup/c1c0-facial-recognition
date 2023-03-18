
build:
	venv/bin/python -m build --wheel

run: build
	venv/bin/python -m r2_facial_recognition.client -l -D

new_run: install run

new_test: install test

test: build
	venv/bin/python tests/basic_test.py

clean:
	rm -rf ./build ./dist ./*egg-info
	
install: clean build
	venv/bin/pip install --force-reinstall dist/r2_facial_recognition-*-py3-none-any.whl
