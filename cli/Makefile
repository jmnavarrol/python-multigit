SHELL := /bin/bash

PYTHON ?= python3
UPLOADER = python3 -m twine upload

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_NC := \033[0m

.PHONY: help targets test build doc upload-tmp clean

help: targets

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}help | targets:${C_NC} show this menu."
	@echo -e "\t${C_BOLD}test:${C_NC} run the CLI unit tests."
	@echo -e "\t${C_BOLD}build:${C_NC} build the CLI package with hatchling after test/doc gates."
	@echo -e "\t${C_BOLD}doc:${C_NC} build the CLI Sphinx documentation."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} upload CLI artifacts to TestPyPI."
# 	@echo -e "\t${C_BOLD}upload:${C_NC} upload CLI artifacts to PyPI."
	@echo -e "\t${C_BOLD}clean:${C_NC} remove CLI build artifacts."

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

build: test doc
	$(PYTHON) -m hatchling build

doc:
	sphinx-build -b html docs docs/build/sphinx-doc/html
	sphinx-build -b linkcheck docs docs/build/sphinx-doc/linkcheck

upload-tmp: build
	$(UPLOADER) --repository testpypi dist/*

# upload: build
# 	$(UPLOADER) --repository pypi dist/*

clean:
	rm -rf build dist *.egg-info
