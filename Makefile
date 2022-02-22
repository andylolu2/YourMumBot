-include .env
export

DISCORD_CHAT_EXPORTER_DIR = "lib/discord-chat-exporter"
STANFORD_CORENLP_DIR = "lib/stanford-corenlp"
RAW_DATA_DIR := "data/raw/ext"
DOCKER_NAME := yourmumbot
DOCKER_TAG := $(DOCKER_NAME):latest
DOCKER_MEM_MAX := "700m"
DOCKER_CPU_MAX := "1.5" # 1024 * 3 / 4

EC2_IP := $(shell terraform -chdir=terraform output -raw instance_ip)
SSH_TARGET := root@$(EC2_IP)
SSH_URL := "ssh://$(SSH_TARGET)"

clean-data:
	@rm -rf $(RAW_DATA_DIR)

clean-logs:
	@find . -type f -wholename "**/logs/**" -delete

clean-tmps:
	@find . -type f -name "*.props" -delete

clean-docker:
	@docker rmi $(DOCKER_TAG)

clean-all: clean-data clean-logs clean-tmps

gh-login:
	@echo $(CR_PAT) | docker login $(GHCR_PREFIX) -u $(GH_USER_NAME) --password-stdin

dh-login:
	@echo $(DH_PW) | docker login -u $(DH_USER_NAME) --password-stdin

run:
	@cd src && python -m bot.main

run-api:
	@cd src && uvicorn api.main:app --reload
	
docker-build:
	@echo "Building docker image..."
	@docker-compose -p $(DOCKER_NAME) build
	@docker image prune -f

docker-push:
	@echo "Pushing docker image..."
	@docker-compose -p $(DOCKER_NAME) push

docker-run: docker-stop
	@ENV=$(ENV) \
		DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) \
		docker-compose --compatibility -p $(DOCKER_NAME) up -d

docker-stop:
	@docker-compose --compatibility -p $(DOCKER_NAME) down

docker-run-server:
	@docker-compose --compatibility -p $(DOCKER_NAME) up -d corenlp languagetools

docker-stop-server:
	@docker-compose -p $(DOCKER_NAME) stop corenlp languagetools
	@docker-compose -p $(DOCKER_NAME) rm -f corenlp languagetools

docker-build-api:
	@docker-compose -p $(DOCKER_NAME) build corenlp languagetools api

docker-run-api:
	@docker-compose --compatibility -p $(DOCKER_NAME) up -d corenlp languagetools api

docker-stop-api:
	@docker-compose -p $(DOCKER_NAME) stop corenlp languagetools api
	@docker-compose -p $(DOCKER_NAME) rm -f corenlp languagetools api

docker-shell:
	@docker exec -it $(DOCKER_NAME) /bin/bash

docker-stats:
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

docker-log:
	@docker logs $(DOCKER_NAME)

docker-logs:
	@docker-compose -p $(DOCKER_NAME) logs

build:
	@$(MAKE) docker-build
	@$(MAKE) docker-push 

ssh-add-known-host:
	ssh-keyscan -H $(EC2_IP) >> ~/.ssh/known_hosts

ssh-instance:
	@ssh $(SSH_TARGET) "$(CMD)"

deploy-pull:
	@echo "Pulling image..."
	docker-compose -p $(DOCKER_NAME) -H $(SSH_URL) pull

deploy-clean:
	@echo "Stopping current containers..."
	docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) down
	docker -H $(SSH_URL) image prune -f
	
deploy-run:
	@ENV=PROD DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) \
		docker-compose --compatibility -p $(DOCKER_NAME) -H $(SSH_URL) up -d --no-build

deploy:
	@$(MAKE) deploy-pull
	@$(MAKE) deploy-clean
	@$(MAKE) deploy-run

deploy-log:
	@docker-compose -p $(DOCKER_NAME) -H $(SSH_URL) logs api

deploy-stats:
	@docker -H $(SSH_URL) stats \
		--format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

terraform-%:
	terraform -chdir=terraform $*
