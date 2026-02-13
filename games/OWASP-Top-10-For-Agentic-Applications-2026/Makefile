COMPOSE ?= docker compose

.PHONY: help up init run-asi01 run-asi02 run-asi03 course-list down

help:
	@echo "Targets:"
	@echo "  make course-list                # List available courses"
	@echo "  make run-asi01                  # Run ASI01 course"
	@echo "  make run-asi02                  # Run ASI02 course"
	@echo "  make run-asi03                  # Run ASI03 course"
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
