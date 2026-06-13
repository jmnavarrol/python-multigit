# Makefile for python-multigit (dual-distribution project)
# Builds both multigit-lib (library) and multigit (CLI)

SHELL := /bin/bash

SOURCE_DIR = $(CURDIR)/src/
LIB_DIR = $(CURDIR)/lib/

BUILD_DIR = $(CURDIR)/build/

PYTHON_FILES = $(shell find ${SOURCE_DIR} ${LIB_DIR} -type f -name '*.py')
OTHER_INCLUDES = $(SOURCE_DIR)LICENSE $(LIB_DIR)LICENSE $(SOURCE_DIR)README.md $(LIB_DIR)README.md

SDIST_FILES = $(BUILD_DIR)/dist/*.tar.gz
WHEELS = $(BUILD_DIR)/dist/*.whl

SPHINXDIR = $(SOURCE_DIR)sphinx
SPHINX_OUTPUT = $(BUILD_DIR)sphinx-doc

UPTOOL = python -m twine upload


# Style table
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_YELLOW := \033[1;1;33m
export C_RED := \033[1;31m
export C_NC := \033[0m

# Basic targets
.PHONY: targets date test test-lib test-cli build build-lib build-cli doc clean

targets:
	@echo -e "${C_BOLD}Main targets for python-multigit (dual-distribution):${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} this one (default)."
	@echo -e "\t${C_BOLD}date:${C_NC} shows date in CHANGELOG format."
	@echo -e "\t${C_BOLD}test:${C_NC} runs unit tests for both library and CLI."
	@echo -e "\t${C_BOLD}test-lib:${C_NC} runs unit tests for library only."
	@echo -e "\t${C_BOLD}test-cli:${C_NC} runs unit tests for CLI only."
	@echo -e "\t${C_BOLD}build:${C_NC} builds both distributions (sdist, wheels) and Sphinx docs."
	@echo -e "\t${C_BOLD}build-lib:${C_NC} builds library distribution only."
	@echo -e "\t${C_BOLD}build-cli:${C_NC} builds CLI distribution only."
	@echo -e "\t${C_BOLD}doc:${C_NC} builds HTML Sphinx docs."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} uploads both versions to testing PyPI service."
	@echo -e "\t${C_BOLD}upload:${C_NC} uploads both versions to live PyPI service."
	@echo -e "\t${C_BOLD}clean:${C_NC} deletes temp files and build outputs."

date:
	@formated_date=`LC_ALL=C date +"%Y-%^b-%d"` \
	&& echo -e "$${C_BOLD}Changelog date is:$${C_NC} $${C_GREEN}$${formated_date}$${C_NC}"

# Test targets
test: test-lib test-cli

test-lib:
	@echo -e "${C_BOLD}Testing multigit-lib...${C_NC}"
	python -m unittest discover --start-directory ${LIB_DIR}src/tests

test-cli:
	@echo -e "${C_BOLD}Testing multigit CLI...${C_NC}"
	python -m unittest discover --start-directory ${SOURCE_DIR}tests

# Build targets
build: test build-lib build-cli doc

build-lib: test-lib $(SDIST_FILES) $(WHEELS)
	@echo -e "${C_BOLD}Building multigit-lib...${C_NC}"
	cd lib && hatch build

build-cli: test-cli $(SDIST_FILES) $(WHEELS)
	@echo -e "${C_BOLD}Building multigit CLI...${C_NC}"
	hatch build

$(SDIST_FILES): $(PYTHON_FILES) $(OTHER_INCLUDES)
	hatch build --target sdist

$(WHEELS): $(PYTHON_FILES) $(OTHER_INCLUDES)
	hatch build --target wheel

doc:
	$(MAKE) BUILDDIR=${SPHINX_OUTPUT} html --directory=$(SPHINXDIR)
	$(MAKE) BUILDDIR=${SPHINX_OUTPUT} linkcheck --directory=$(SPHINXDIR)

upload-tmp: clean build
	$(UPTOOL) --repository testpypi $(CURDIR)/dist/* $(LIB_DIR)dist/*

upload: clean build
	$(UPTOOL) --repository pypi $(CURDIR)/dist/* $(LIB_DIR)dist/*

clean:
	@$(MAKE) clean --directory=$(SPHINXDIR)
	rm -rf ${BUILD_DIR} dist/ lib/dist/
	find -type f -name '*.pyc' -exec rm -f '{}' \;
	find -type d -name '__pycache__' | xargs rm -rf
	rm -rf src/tests/scenarios lib/src/tests/scenarios
	rm -rf ../projects
