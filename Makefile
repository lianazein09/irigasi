ENV_FILE ?= .env
COMPOSE := docker compose --env-file $(ENV_FILE)
CLEAN_DEPLOY := $(filter --clean,$(MAKECMDGOALS))

.PHONY: help deploy up down restart build rebuild logs ps config clean --clean

help:
	@echo "Available targets:"
	@echo "  make deploy            - Deploy with rebuild"
	@echo "  make deploy --clean    - Clean deploy with fresh images and volumes reset"
	@echo "  make up       - Start existing containers without rebuild"
	@echo "  make down     - Stop containers"
	@echo "  make restart  - Restart containers"
	@echo "  make build    - Build images only"
	@echo "  make rebuild  - Rebuild and start containers"
	@echo "  make logs     - Follow container logs"
	@echo "  make ps       - Show container status"
	@echo "  make config   - Render merged compose config"
	@echo "  make clean    - Stop stack and remove volumes"
	@echo ""
	@echo "Override env file with: make <target> ENV_FILE=.env.example"

deploy:
	@echo "Removing local frontend build artifacts (dist/) to avoid stale assets..."
	@rm -rf dist || true
ifeq ($(CLEAN_DEPLOY),--clean)
	@echo "Running clean deploy: stopping stack and removing volumes..."
	$(COMPOSE) down -v --remove-orphans || true
endif
	@echo "Removing existing app images if present..."
	@docker image rm --force irigasi-frontend irigasi-backend irigasi-mqtt-worker || true
	@echo "Pruning unused Docker objects to avoid stale cache..."
	@docker system prune -af || true
	@echo "Building fresh app images (no cache)..."
	$(COMPOSE) build --no-cache backend mqtt-worker frontend
	@echo "Starting stack with rebuilt images..."
	$(COMPOSE) up -d --force-recreate --build
	@echo "Waiting a few seconds for containers to settle..."
	@sleep 5
	$(COMPOSE) ps
	@echo "If backend is restarting or unhealthy, view recent backend logs:"
	@echo "  make logs  # or: docker compose logs --tail 80 backend"

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) up -d --build

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

config:
	$(COMPOSE) config

clean:
	$(COMPOSE) down -v

--clean:
	@:
