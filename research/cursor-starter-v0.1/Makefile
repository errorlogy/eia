.PHONY: demo eoi test check

demo:
	PYTHONPATH=src python -m eia demo

eoi:
	PYTHONPATH=src python -m eia eoi-demo

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

check: test
	PYTHONPATH=src python -m compileall -q src tests

