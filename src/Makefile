# Makefile for python-multigit
SHELL := /bin/bash

PYTOOL = python -m build
PYTHON_FILES = $(shell find . -type f -name '*.py')
OTHER_INCLUDES = LICENSE README.md MANIFEST.in
SDIST_FILES = dist/*.tar.gz
WHEELS = dist/*.whl
UPTOOL = python -m twine upload

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_YELLOW := \033[1;1;33m
export C_RED := \033[1;31m
export C_NC := \033[0m

# Basic targets
.PHONY: targets build clean

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} this one (default)."
	@echo -e "\t${C_BOLD}build:${C_NC} builds source tarball and binary egg (sdist, wheels)."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} uploads version to testing PyPi service."
	@echo -e "\t${C_BOLD}upload:${C_NC} uploads version to live PyPi service."
	@echo -e "\t${C_BOLD}clean:${C_NC} deletes temp files."
	
build: $(SDIST_FILES) $(WHEELS)

$(SDIST_FILES): $(PYTHON_FILES) $(OTHER_INCLUDES)
	$(PYTOOL) --sdist
	
$(WHEELS): $(PYTHON_FILES) $(OTHER_INCLUDES)
	$(PYTOOL) --wheel
	
upload-tmp: build
	$(UPTOOL) --repository testpypi dist/*
	
upload: build
	$(UPTOOL) --repository pypi dist/*
	
clean:
	rm -rf MANIFEST build dist *.egg-info
	find -type f -name '*.pyc' -exec rm -f '{}' \;
	find -type d -name '__pycache__' | xargs rm -rf
	rm -rf ../projects
	