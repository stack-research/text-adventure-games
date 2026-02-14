COMPOSE ?= docker compose

.PHONY: help up init run-asi01 run-asi02 run-asi03 run-asi04 run-asi05 run-asi06 run-asi07 run-asi08 course-list down

help:
	@echo "Targets:"
	@echo "  make course-list                # List available courses"
	@echo "  make run-asi01                  # Run ASI01 course"
	@echo "  make run-asi02                  # Run ASI02 course"
	@echo "  make run-asi03                  # Run ASI03 course"
	@echo "  make run-asi04                  # Run ASI04 course"
	@echo "  make run-asi05                  # Run ASI05 course"
	@echo "  make run-asi06                  # Run ASI06 course"
	@echo "  make run-asi07                  # Run ASI07 course"
	@echo "  make run-asi08                  # Run ASI08 course"
	@echo "  make up                         # Start support services"
	@echo "  make init                       # Pull/initialize LLM model"
	@echo "  make down                       # Stop all services"

up:
	$(COMPOSE) up -d ollama db api mail

init: up
	$(COMPOSE) up ollama-init

run-asi01: init
	COURSE=ASI01-Agent-Goal-Hijack $(COMPOSE) run --rm game

run-asi02: init
	COURSE=ASI02-Tool-Misuse-and-Exploitation $(COMPOSE) run --rm game

run-asi03: init
	COURSE=ASI03-Identity-and-Privilege-Abuse $(COMPOSE) run --rm game

run-asi04: init
	COURSE=ASI04-Agentic-Supply-Chain-Vulnerabilities $(COMPOSE) run --rm game

run-asi05: init
	COURSE=ASI05-Unexpected-Code-Execution-RCE $(COMPOSE) run --rm game

run-asi06: init
	COURSE=ASI06-Memory-and-Context-Poisoning $(COMPOSE) run --rm game

run-asi07: init
	COURSE=ASI07-Insecure-Inter-Agent-Communication $(COMPOSE) run --rm game

run-asi08: init
	COURSE=ASI08-Cascading-Failures $(COMPOSE) run --rm game

course-list:
	@find courses -mindepth 1 -maxdepth 1 -type d -exec basename {} \; \
		| grep -E '^ASI[0-9]{2}-' \
		| sort \
		| while read -r course; do \
			run_target=$$(printf "%s" "$$course" | cut -d- -f1 | tr '[:upper:]' '[:lower:]'); \
			printf "%s -> make run-%s\n" "$$course" "$$run_target"; \
		done

down:
	$(COMPOSE) down
