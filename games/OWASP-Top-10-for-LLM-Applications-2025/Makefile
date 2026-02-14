COMPOSE ?= docker compose

.PHONY: help up init run-llm01 course-list down

help:
	@echo "Targets:"
	@echo "  make course-list                # List available courses"
	@echo "  make run-llm01                  # Run LLM01 course"
	@echo "  make up                         # Start support services"
	@echo "  make init                       # Pull/initialize LLM model"
	@echo "  make down                       # Stop all services"

up:
	$(COMPOSE) up -d ollama db api mail

init: up
	$(COMPOSE) up ollama-init

run-llm01: init
	COURSE=LLM01-Prompt-Injection $(COMPOSE) run --rm game

course-list:
	@find courses -mindepth 1 -maxdepth 1 -type d -exec basename {} \; \
		| grep -E '^LLM[0-9]{2}-' \
		| sort \
		| while read -r course; do \
			run_target=$$(printf "%s" "$$course" | cut -d- -f1 | tr '[:upper:]' '[:lower:]'); \
			printf "%s -> make run-%s\n" "$$course" "$$run_target"; \
		done

down:
	$(COMPOSE) down
