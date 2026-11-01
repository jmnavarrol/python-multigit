# Root Makefile: recursive orchestration for independently packaged components.
SHELL := /bin/bash

# Color codes
export C_BOLD := \033[1m
export C_GREEN := \033[1;32m
export C_NC := \033[0m

.PHONY: targets date test build doc clean \
	lib-test lib-build lib-doc lib-clean \
	cli-test cli-build cli-doc cli-clean

targets:
	@echo -e "${C_BOLD}Root orchestration targets:${C_NC}"
	@echo -e "\t${C_BOLD}date:${C_NC} show date in CHANGELOG format."
	@echo -e "\t${C_BOLD}test:${C_NC} run lib and CLI offline suites."
	@echo -e "\t${C_BOLD}build:${C_NC} build both components after their quality gates."
	@echo -e "\t${C_BOLD}doc:${C_NC} build both component documentation sets."
	@echo -e "\t${C_BOLD}clean:${C_NC} clean root and component build artifacts."

date:
	@formated_date=`LC_ALL=C date +"%Y-%^b-%d"` \
	&& echo -e "$${C_BOLD}Changelog date is:$${C_NC} $${C_GREEN}$${formated_date}$${C_NC}"

test: lib-test cli-test

build: lib-build cli-build

doc: lib-doc cli-doc

clean:
	rm -rf $(CURDIR)/build/
	$(MAKE) -C lib clean
	$(MAKE) -C cli clean

lib-test:
	$(MAKE) -C lib test

lib-build:
	$(MAKE) -C lib build

lib-doc:
	$(MAKE) -C lib doc

lib-clean:
	$(MAKE) -C lib clean

cli-test:
	$(MAKE) -C cli test

cli-build:
	$(MAKE) -C cli build

cli-doc:
	$(MAKE) -C cli doc

cli-clean:
	$(MAKE) -C cli clean
