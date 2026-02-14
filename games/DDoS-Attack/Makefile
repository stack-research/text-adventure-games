COMPOSE ?= docker compose

.PHONY: help build up run down logs ps restart clean

help:
	@echo "Targets:"
	@echo "  make build    - Build game image"
	@echo "  make up       - Start full stack (ollama + model pull + game)"
	@echo "  make run      - Run an interactive game session"
	@echo "  make down     - Stop stack"
	@echo "  make logs     - Tail compose logs"
	@echo "  make ps       - Show service status"
	@echo "  make restart  - Restart stack"
	@echo "  make clean    - Stop stack and remove volumes"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build

run:
	$(COMPOSE) run --rm game

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

restart: down up

clean:
	$(COMPOSE) down -v
