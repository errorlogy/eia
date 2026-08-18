.PHONY: demo eoi woe test check

demo:
	PYTHONPATH=src python -m eia demo

eoi:
	PYTHONPATH=src python -m eia eoi-demo

woe:
	PYTHONPATH=src python -m eia woe-demo

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

check: test
	PYTHONPATH=src python -m compileall -q src tests
