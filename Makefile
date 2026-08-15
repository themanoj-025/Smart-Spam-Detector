# ═══════════════════════════════════════════════════════════════════════
# Smart-Spam-Detector — ergonomic Docker entry points
# ═══════════════════════════════════════════════════════════════════════

DOCKER_COMPOSE := docker compose

.PHONY: help up down logs ps build shell test lint health config clean reset

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

up: ## Start the stack (dev override with source mounts + hot reload)
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d

down: ## Stop the stack
	$(DOCKER_COMPOSE) down

logs: ## Tail logs from both services
	$(DOCKER_COMPOSE) logs -f --tail=100

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

build: ## Build images (dev target)
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build

shell: ## Open a shell in the api container
	$(DOCKER_COMPOSE) exec api /bin/sh

api-shell: ## Alias for shell
	$(DOCKER_COMPOSE) exec api /bin/sh

ui-shell: ## Open a shell in the streamlit container
	$(DOCKER_COMPOSE) exec streamlit /bin/sh

test: ## Run the test suite inside the dev image
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm api python -m pytest tests/ -v --tb=short

lint: ## Compile-check all Python files
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm api sh -c "python -m compileall -q api.py app.py src && echo OK"

health: ## Check API + UI health endpoints
	curl -fsS http://localhost:8000/health
	curl -fsS http://localhost:8501/_stcore/health

config: ## Validate compose files
	$(DOCKER_COMPOSE) config

clean: ## Stop and remove containers + volumes (history DB loss!)
	$(DOCKER_COMPOSE) down -v --remove-orphans

reset: clean ## Full rebuild from scratch
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d
