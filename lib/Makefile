# Makefile for python-multigit/lib PoC
SHELL := /bin/bash

PYPROJECT_FILE = pyproject.toml
README_FILE = README.md
PYTHON_FILES = $(shell find src -type f -name '*.py')
TEST_FILES = $(shell find tests -type f -name '*.py')
VERSION = $(shell sed -nE 's/^__version__ = "([^"]+)"/\1/p' src/multigit_lib/__init__.py)
DIST_DIR = dist
BUILD_DIR = $(CURDIR)/build
TEST_LOG = $(BUILD_DIR)/test.log
SPHINXDIR = docs
SPHINX_OUTPUT = $(BUILD_DIR)/sphinx-doc
DOC_FILES = $(shell find $(SPHINXDIR) -type f \( -name '*.rst' -o -name '*.py' -o -name 'Makefile' \))
DOC_INDEX = $(SPHINX_OUTPUT)/html/index.html
SDIST_FILE = $(DIST_DIR)/multigit_lib-$(VERSION).tar.gz
WHEEL_FILE = $(DIST_DIR)/multigit_lib-$(VERSION)-py3-none-any.whl
BUILD_INPUTS = $(PYPROJECT_FILE) $(README_FILE) $(PYTHON_FILES)
TEST_INPUTS = $(PYTHON_FILES) $(TEST_FILES)
DOC_INPUTS = $(DOC_FILES) $(PYTHON_FILES)

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_NC := \033[0m

# Basic targets
.PHONY: help targets test build doc clean

help: targets

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} show this help."
	@echo -e "\t${C_BOLD}test:${C_NC} run offline unittest smoke tests when inputs change."
	@echo -e "\t${C_BOLD}build:${C_NC} build sdist and wheel for lib."
	@echo -e "\t${C_BOLD}doc:${C_NC} build HTML Sphinx docs recursively from docs/."
	@echo -e "\t${C_BOLD}clean:${C_NC} remove local build artifacts."

test: $(TEST_LOG)

$(TEST_LOG): $(TEST_INPUTS)
	@mkdir -p $(BUILD_DIR)
	PYTHONPATH=src python3 -m unittest discover --start-directory tests > $(TEST_LOG)

build: test doc $(SDIST_FILE) $(WHEEL_FILE)

$(SDIST_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target sdist

$(WHEEL_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target wheel

doc: $(DOC_INDEX)

$(DOC_INDEX): $(DOC_INPUTS)
	$(MAKE) BUILDDIR=$(SPHINX_OUTPUT) html --directory=$(SPHINXDIR)

clean:
	rm -rf $(DIST_DIR)/ $(BUILD_DIR)/
