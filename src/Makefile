# Makefile for python-multigit
SHELL := /bin/bash

PYTOOL = python -m build
PYTHON_FILES = $(shell find . -not \( -path './build/*' -prune \) -type f -name '*.py')
OTHER_INCLUDES = LICENSE README.md MANIFEST.in
SDIST_FILES = dist/*.tar.gz
SPHINXDIR = sphinx
WHEELS = dist/*.whl
UPTOOL = python -m twine upload

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_YELLOW := \033[1;1;33m
export C_RED := \033[1;31m
export C_NC := \033[0m

# Basic targets
.PHONY: targets test build clean doc

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} this one (default)."
	@echo -e "\t${C_BOLD}test:${C_NC} runs unit tests."
	@echo -e "\t${C_BOLD}build:${C_NC} builds source tarball, binary egg (sdist, wheels) and HTML sphinx docs."
	@echo -e "\t${C_BOLD}doc:${C_NC} builds HTML sphinx docs."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} uploads version to testing PyPi service."
	@echo -e "\t${C_BOLD}upload:${C_NC} uploads version to live PyPi service."
	@echo -e "\t${C_BOLD}clean:${C_NC} deletes temp files."

test:
	python -m unittest discover -s tests

build: test $(SDIST_FILES) $(WHEELS) doc

$(SDIST_FILES): $(PYTHON_FILES) $(OTHER_INCLUDES)
	python -m build --sdist

$(WHEELS): $(PYTHON_FILES) $(OTHER_INCLUDES)
	python -m build --wheel

doc:
	@$(MAKE) html --directory=$(SPHINXDIR)
	@$(MAKE) linkcheck --directory=$(SPHINXDIR)

upload-tmp: clean build
	$(UPTOOL) --repository testpypi dist/*

upload: clean build
	$(UPTOOL) --repository pypi dist/*

clean:
	@$(MAKE) clean --directory=$(SPHINXDIR)
	rm -rf MANIFEST build dist *.egg-info
	find -type f -name '*.pyc' -exec rm -f '{}' \;
	find -type d -name '__pycache__' | xargs rm -rf
	rm -rf tests/scenarios
	rm -rf ../projects
