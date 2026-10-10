# Makefile for python-multigit
SHELL := /bin/bash

SOURCE_DIR = $(CURDIR)/src/
BUILD_DIR = $(CURDIR)/build/

PYTHON_FILES = $(shell find ${SOURCE_DIR} -type f -name '*.py')
OTHER_INCLUDES = $(SOURCE_DIR)LICENSE $(SOURCE_DIR)README.md

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
.PHONY: targets date test clean doc upload-tmp \
	lib-test lib-build lib-doc lib-upload-tmp lib-clean \
	cli-test cli-build cli-doc cli-upload-tmp cli-clean

# Legacy root workflow retained for backward compatibility.
targets:
	@echo -e "${C_BOLD}Main targets are:${C_NC}"
	@echo -e "\t${C_BOLD}targets:${C_NC} this one (default)."
	@echo -e "\t$${C_BOLD}date:$${C_NC} shows date in CHANGELOG format."
	@echo -e "\t${C_BOLD}test:${C_NC} runs unit tests."
	@echo -e "\t${C_BOLD}build:${C_NC} builds source tarball, binary egg (sdist, wheels) and HTML sphinx docs."
	@echo -e "\t${C_BOLD}doc:${C_NC} builds HTML sphinx docs."
	@echo -e "\t${C_BOLD}upload-tmp:${C_NC} uploads version to testing PyPi service."
#	@echo -e "\t${C_BOLD}upload:${C_NC} uploads version to live PyPi service."
	@echo -e "\t${C_BOLD}clean:${C_NC} deletes temp files."
	@echo -e "\t${C_BOLD}lib-test:${C_NC} runs the library test suite in lib/."
	@echo -e "\t${C_BOLD}lib-build:${C_NC} builds the library package via lib/Makefile."
	@echo -e "\t${C_BOLD}lib-doc:${C_NC} builds the library documentation via lib/Makefile."
	@echo -e "\t${C_BOLD}lib-upload-tmp:${C_NC} uploads the library to TestPyPI via lib/Makefile."
#	@echo -e "\t${C_BOLD}lib-upload:${C_NC} uploads the library to PyPI via lib/Makefile."
	@echo -e "\t${C_BOLD}cli-test:${C_NC} runs the CLI test suite in cli/."
	@echo -e "\t${C_BOLD}cli-build:${C_NC} builds the CLI package via cli/Makefile."
	@echo -e "\t${C_BOLD}cli-doc:${C_NC} builds the CLI documentation via cli/Makefile."
	@echo -e "\t${C_BOLD}cli-upload-tmp:${C_NC} uploads the CLI to TestPyPI via cli/Makefile."
#	@echo -e "\t${C_BOLD}cli-upload:${C_NC} uploads the CLI to PyPI via cli/Makefile."

date:
	@formated_date=`LC_ALL=C date +"%Y-%^b-%d"` \
	&& echo -e "$${C_BOLD}Changelog date is:$${C_NC} $${C_GREEN}$${formated_date}$${C_NC}"

test:
	python -m unittest discover --start-directory ${SOURCE_DIR}tests

build: test $(SDIST_FILES) $(WHEELS) doc

$(SDIST_FILES): $(PYTHON_FILES) $(OTHER_INCLUDES)
	hatch build --target sdist

$(WHEELS): $(PYTHON_FILES) $(OTHER_INCLUDES)
	hatch build --target wheel

doc:
	$(MAKE) BUILDDIR=${SPHINX_OUTPUT} html --directory=$(SPHINXDIR)
	$(MAKE) BUILDDIR=${SPHINX_OUTPUT} linkcheck --directory=$(SPHINXDIR)

upload-tmp: clean build
	$(UPTOOL) --repository testpypi $(CURDIR)/dist/*

# upload: clean build
# 	$(UPTOOL) --repository pypi $(CURDIR)/dist/*

clean:
	@$(MAKE) clean --directory=$(SPHINXDIR)
	rm -rf ${BUILD_DIR} dist/
	find -type f -name '*.pyc' -exec rm -f '{}' \;
	find -type d -name '__pycache__' | xargs rm -rf
	rm -rf tests/scenarios
	rm -rf ../projects
	$(MAKE) -C lib clean
	$(MAKE) -C cli clean

# New split-package targets delegated to the component Makefiles.
lib-test:
	$(MAKE) -C lib test

lib-build: lib-test lib-doc
	$(MAKE) -C lib build

lib-doc:
	$(MAKE) -C lib doc

lib-upload-tmp: lib-build
	$(MAKE) -C lib upload-tmp

# lib-upload: lib-build
#	$(MAKE) -C lib upload

lib-clean:
	$(MAKE) -C lib clean

cli-test:
	$(MAKE) -C cli test

cli-build: cli-test cli-doc
	$(MAKE) -C cli build

cli-doc:
	$(MAKE) -C cli doc

cli-upload-tmp: cli-build
	$(MAKE) -C cli upload-tmp

# cli-upload: cli-build
#	$(MAKE) -C cli upload

cli-clean:
	$(MAKE) -C cli clean
