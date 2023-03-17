
build:
	venv/bin/python -m build --wheel
	venv/bin/pip install --force-reinstall dist/r2_facial_recognition-*-py3-none-any.whl

run: build
	venv/bin/python -m r2_facial_recognition.client -l -D

test: build
	venv/bin/python tests/basic_test.py

clean:
	rm -rf ./build ./dist ./*egg-info
	
