# Makefile for python-multigit/lib PoC
SHELL := /bin/bash

PYPROJECT_FILE = pyproject.toml
README_FILE = README.md
PYTHON_FILES = $(shell find src -type f -name '*.py')
VERSION = $(shell sed -nE 's/^__version__ = "([^"]+)"/\1/p' src/multigit_lib/__init__.py)
DIST_DIR = dist
SDIST_FILE = $(DIST_DIR)/multigit_lib-$(VERSION).tar.gz
WHEEL_FILE = $(DIST_DIR)/multigit_lib-$(VERSION)-py3-none-any.whl
BUILD_INPUTS = $(PYPROJECT_FILE) $(README_FILE) $(PYTHON_FILES)

# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_NC := \033[0m

# Basic targets
.PHONY: help targets build clean

help: targets

targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} show this help."
	@echo -e "\t${C_BOLD}build:${C_NC} build sdist and wheel for lib."
	@echo -e "\t${C_BOLD}clean:${C_NC} remove local build artifacts."

build: $(SDIST_FILE) $(WHEEL_FILE)

$(SDIST_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target sdist

$(WHEEL_FILE): $(BUILD_INPUTS)
	python3 -m hatchling build --target wheel

clean:
	rm -rf dist/ build/
