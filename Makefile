-include .env
export

DOCKER_NAME := yourmumbot

# EC2_IP := $(shell terraform -chdir=terraform output -raw instance_ip)
# SSH_TARGET := root@$(EC2_IP)
# SSH_URL := "ssh://$(SSH_TARGET)"


do-dev-deploy:
	doctl serverless connect your-mum-bot-dev
	doctl serverless deploy . --env .dev.env --remote-build

do-dev-url:
	@doctl serverless connect your-mum-bot-dev > /dev/null
	@doctl serverless function get bot/your_mum --url

do-prod-deploy:
	doctl serverless connect your-mum-bot-prod
	doctl serverless deploy . --env .prod.env --remote-build

do-prod-url:
	@doctl serverless connect your-mum-bot-prod > /dev/null
	@doctl serverless function get bot/your_mum --url

gh-login:
	@echo $(CR_PAT) | docker login $(GHCR_PREFIX) -u $(GH_USER_NAME) --password-stdin

dh-login:
	@echo $(DH_PW) | docker login -u $(DH_USER_NAME) --password-stdin

run-bot:
	cd src && python -m bot.main

run-api:
	cd src && uvicorn api.main:app --port $(API_PORT) --host 127.0.0.1
	
docker-build:
	@echo "Building docker image..."
	docker-compose --compatibility -p $(DOCKER_NAME) build
	docker image prune -f

docker-push: docker-build
	@echo "Pushing docker image..."
	docker-compose --compatibility -p $(DOCKER_NAME) push

docker-run: docker-stop
	docker-compose --compatibility -p $(DOCKER_NAME) up -d

docker-stop:
	docker-compose --compatibility -p $(DOCKER_NAME) down

docker-run-server: docker-stop-server
	docker-compose --compatibility -p $(DOCKER_NAME) up -d corenlp languagetools

docker-stop-server:
	docker-compose --compatibility -p $(DOCKER_NAME) stop corenlp languagetools
	docker-compose --compatibility -p $(DOCKER_NAME) rm -f corenlp languagetools

docker-build-api:
	docker-compose --compatibility -p $(DOCKER_NAME) build corenlp languagetools api

docker-run-api:
	docker-compose --compatibility -p $(DOCKER_NAME) up -d corenlp languagetools api

docker-stop-api:
	docker-compose --compatibility -p $(DOCKER_NAME) stop corenlp languagetools api
	docker-compose --compatibility -p $(DOCKER_NAME) rm -f corenlp languagetools api

docker-shell:
	docker exec -it $(DOCKER_NAME) /bin/bash

docker-stats:
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

docker-logs:
	docker-compose --compatibility -p $(DOCKER_NAME) logs --follow --tail=10 bot api prometheus

build: docker-build docker-push

ssh-add-known-host:
	ssh-keyscan -H $(EC2_IP) >> ~/.ssh/known_hosts

ssh-instance:
	@ssh $(SSH_TARGET) "$(CMD)"

deploy-pull:
	@echo "Pulling images..."
	docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) pull

deploy-setup: env-sub-config env-sub-web
	@echo "Setting up prometheus files..."
	ssh $(SSH_TARGET) "mkdir -p prometheus"
	scp prometheus/config.secret.yml $(SSH_TARGET):prometheus/config.secret.yml
	scp prometheus/web.secret.yml $(SSH_TARGET):prometheus/web.secret.yml

deploy-clean: deploy-pull
	@echo "Stopping current containers..."
	docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) down
	docker -H $(SSH_URL) image prune -f
	
deploy-run: deploy-setup deploy-pull
	@echo "Starting new containers..."
	ENV=PROD API_PORT=80 PROM_PATH=/root \
		docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) up -d --no-build

deploy: deploy-setup deploy-pull deploy-clean deploy-run

deploy-logs:
	docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) logs \
		--follow --tail=10 bot api prometheus

deploy-stats:
	@docker -H $(SSH_URL) stats \
		--format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

terraform-%:
	terraform -chdir=terraform $*

env-sub-config:
	envsubst < prometheus/config.yml > prometheus/config.secret.yml

env-sub-web:
	envsubst < prometheus/web.yml > prometheus/web.secret.yml
