# Makefile for python-multigit/lib PoC
SHELL := /bin/bash

PYPROJECT_FILE = pyproject.toml
README_FILE = README.md
PYTHON_FILES = $(shell find src -type f -name '*.py')
TEST_FILES = $(shell find tests -type f -name '*.py')
VERSION = $(shell sed -nE 's/^__version__ = "([^"]+)"/\1/p' src/multigit_lib/__init__.py)
DIST_DIR = dist
BUILD_DIR = $(CURDIR)/build
SPHINXDIR = docs
SPHINX_OUTPUT = $(BUILD_DIR)/sphinx-doc
DOC_FILES = $(shell find $(SPHINXDIR) -type f \( -name '*.rst' -o -name '*.py' -o -name 'Makefile' \))
DOC_INDEX = $(SPHINX_OUTPUT)/html/index.html
SDIST_FILE = $(DIST_DIR)/multigit_lib-$(VERSION).tar.gz
WHEEL_FILE = $(DIST_DIR)/multigit_lib-$(VERSION)-py3-none-any.whl
BUILD_INPUTS = $(PYPROJECT_FILE) $(README_FILE) $(PYTHON_FILES)
DOC_INPUTS = $(DOC_FILES) $(PYTHON_FILES)
UPLOADER = python3 -m twine upload

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_NC := \033[0m

# Basic targets
.PHONY: help targets test build doc clean-stale-doc upload-tmp clean

help: targets

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} show this help."
	@echo -e "\t${C_BOLD}test:${C_NC} run the offline unittest suite."
	@echo -e "\t${C_BOLD}build:${C_NC} build sdist and wheel for lib."
	@echo -e "\t${C_BOLD}doc:${C_NC} build HTML Sphinx docs recursively from docs/."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} upload lib artifacts to TestPyPI."
	@echo -e "\t${C_BOLD}clean:${C_NC} remove local build artifacts."

test:
	PYTHONPATH=src python3 -m unittest discover --start-directory tests -v

build: test doc $(SDIST_FILE) $(WHEEL_FILE)

$(SDIST_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target sdist

$(WHEEL_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target wheel

doc: clean-stale-doc $(DOC_INDEX)

clean-stale-doc:
	rm -rf $(SPHINXDIR)/build/

$(DOC_INDEX): $(DOC_INPUTS)
	$(MAKE) BUILDDIR=$(SPHINX_OUTPUT) html --directory=$(SPHINXDIR)
	$(MAKE) BUILDDIR=${SPHINX_OUTPUT} linkcheck --directory=$(SPHINXDIR)

upload-tmp: build
	$(UPLOADER) --repository testpypi $(DIST_DIR)/*

clean:
	rm -rf $(DIST_DIR)/ $(BUILD_DIR)/ $(SPHINXDIR)/build/
