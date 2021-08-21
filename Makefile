-include .env
export

DISCORD_CHAT_EXPORTER_DIR = "lib/discord-chat-exporter"
STANFORD_CORENLP_DIR = "lib/stanford-corenlp"
RAW_DATA_DIR := "data/raw/ext"
DOCKER_NAME := yourmumbot
DOCKER_TAG := $(DOCKER_NAME):latest
DOCKER_MEM_MAX := "700m"
DOCKER_CPU_MAX := "1.5" # 1024 * 3 / 4
DHCR_PREFIX := $(DH_USER_NAME)
GHCR_PREFIX := ghcr.io
TERRAFORM_VARS := "inputVars.tfvars"

EC2_IP := $(shell cd terraform && terraform output instance_ip)
SSH_URL := "ssh://ec2-user@$(EC2_IP)"

check-dotnet-version:
ifeq ($(shell dotnet --version | grep "3\.1\..*"),)
	$(error ".NET must be at version 3.1")
endif

NO_VENV ?= False
check-python-venv:
ifneq ("$(NO_VENV)", "True")
ifeq ("$(VIRTUAL_ENV)","")
	$(error "You should run this in a venv")
endif
endif

check-python-version:
	$(eval PYTHON_MAJOR_VER := $(shell python -V \
		|& grep -oP "[0-9](?=\.[0-9]+\.[0-9]+)" \
		| head -1))
	$(eval PYTHON_MINOR_VER := $(shell python -V \
		|& grep -oP "(?<=[0-9]\.)[0-9]+(?=\.[0-9]+)" \
		| head -1))
	@if [ ! $(PYTHON_MAJOR_VER) -eq 3 ]; \
		then echo "error: python 3 is needed"; \
	else \
		if [ ! $(PYTHON_MINOR_VER) -ge 6 ]; \
			then echo "error: at least python 3.6 is needed"; \
		fi; \
	fi

clean-data:
	@rm -rf $(RAW_DATA_DIR)

clean-logs:
	@find . -type f -wholename "**/logs/**" -delete

clean-tmps:
	@find . -type f -name "*.props" -delete

clean-docker:
	@docker rmi $(DOCKER_TAG)

clean-all: clean-data clean-logs clean-tmps

setup-discord-chat-exporter: check-dotnet-version
	@if [ ! -d $(DISCORD_CHAT_EXPORTER_DIR) ] ; \
	then \
		mkdir -p tmp/ && \
		echo "Downloading DiscordChatExporter..." && \
		wget -c -q https://github.com/Tyrrrz/DiscordChatExporter/releases/latest/download/DiscordChatExporter.CLI.zip -P tmp/; \
		rm -rf $(DISCORD_CHAT_EXPORTER_DIR); \
		mkdir -p $(DISCORD_CHAT_EXPORTER_DIR) && \
		echo "Unzipping..." && \
		unzip -q tmp/DiscordChatExporter.CLI.zip -d $(DISCORD_CHAT_EXPORTER_DIR) && \
		rm -r tmp/; \
	else \
		echo "DiscordChatExporter already exists"; \
	fi;

# deprecated: use build.py instead
setup-stanford-corenlp:
	@if [ ! -d $(STANFORD_CORENLP_DIR) ] ; \
	then \
		mkdir -p tmp/ && \
		echo "Downloading stanford corenlp package..." && \
		wget -c -q -nc --show-progress http://nlp.stanford.edu/software/stanford-corenlp-4.2.2.zip -P tmp/; \
		rm -rf $(STANFORD_CORENLP_DIR); \
		mkdir -p $(STANFORD_CORENLP_DIR) && \
		echo "Unzipping..." && \
		unzip -q tmp/stanford-corenlp-4.2.2.zip -d $(STANFORD_CORENLP_DIR) && \
		rm -r tmp/; \
	else \
		echo "Stanford corenlp already exists"; \
	fi;

run:
	@python -m src.main

run-api:
	@cd src && uvicorn api.main:app --reload

gh-login:
	@echo $(CR_PAT) | docker login $(GHCR_PREFIX) -u $(GH_USER_NAME) --password-stdin

dh-login:
	@echo $(DH_PW) | docker login -u $(DH_USER_NAME) --password-stdin
	
docker-build:
	@echo "Building docker image..."
	@docker-compose -p $(DOCKER_NAME) build
	@docker image prune -f

docker-push:
	@echo "Pushing docker image..."
	@docker-compose -p $(DOCKER_NAME) push

docker-run: docker-stop
	@ENV=PROD \
		DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) \
		docker-compose -p $(DOCKER_NAME) up -d

docker-run-dev: docker-stop
	@ENV=DEV \
		DISCORD_DEV_BOT_TOKEN=$(DISCORD_DEV_BOT_TOKEN) \
		docker-compose -p $(DOCKER_NAME) up -d

docker-run-server:
	@docker-compose -p $(DOCKER_NAME) up -d corenlp languagetools

docker-shell:
	@docker exec -it $(DOCKER_NAME) /bin/bash

docker-stats:
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

docker-log:
	@docker logs $(DOCKER_NAME)

docker-logs:
	@docker-compose -p $(DOCKER_NAME) logs

docker-stop:
	@docker-compose -p $(DOCKER_NAME) down

build:
	@$(MAKE) docker-build
	@$(MAKE) docker-push 

ssh-host:
	@echo $(EC2_IP)

ssh-add-known-host:
	ssh-keyscan -H $(EC2_IP) >> ~/.ssh/known_hosts

ssh-ec2:
	@ssh ec2-user@$(EC2_IP) "$(CMD)"

deploy-setup:
	@$(MAKE) ssh-ec2 CMD='sudo yum update -y && \
		sudo amazon-linux-extras install docker && \
		sudo service docker start && \
		sudo usermod -a -G docker ec2-user && \
		docker info >/dev/null && \
		sudo curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$$$$(uname -s)-$$$$(uname -m) -o /usr/local/bin/docker-compose && \
		sudo chmod +x /usr/local/bin/docker-compose && \
		docker-compose version'

deploy-clean:
	@echo "Stopping..."
	@docker-compose -p $(DOCKER_NAME) -H $(SSH_URL) down
	
deploy-pull:
	@echo "Pulling image..."
	@docker-compose -p $(DOCKER_NAME) -H $(SSH_URL) pull
	
deploy-run:
	@ENV=PROD DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) \
		docker-compose -p $(DOCKER_NAME) -H "ssh://ec2-user@$(EC2_IP)" \
		up -d --no-build

deploy:
	@$(MAKE) deploy-setup
	@$(MAKE) deploy-pull
	@$(MAKE) deploy-clean
	@$(MAKE) deploy-run

deploy-log:
	@docker-compose -p $(DOCKER_NAME) -H "ssh://ec2-user@$(EC2_IP)" logs bot

deploy-stats:
	@docker -H $(SSH_URL) stats \
		--format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}"

# terraform-plan:
# 	@$(MAKE) terraform-cmd CMD="plan -var-file=$(TERRAFORM_VARS)"

# terraform-apply:
# 	@$(MAKE) terraform-cmd CMD="apply -var-file=$(TERRAFORM_VARS)"

# terraform-destory:
# 	@$(MAKE) terraform-cmd CMD="detroy -var-file=$(TERRAFORM_VARS)"

terraform-%:
	terraform -chdir=terraform $* -var-file=$(TERRAFORM_VARS)

terraform-output:
	terraform -chdir=terraform output

CHANNEL_ID ?= 727433810148458498
data-scrape-discord: setup-discord-chat-exporter
	-@rm -rf $(RAW_DATA_DIR)/discord
	@mkdir -p $(RAW_DATA_DIR)/discord
	@dotnet $(DISCORD_CHAT_EXPORTER_DIR)/DiscordChatExporter.Cli.dll \
		export -t $(DISCORD_TOKEN) \
		-c $(CHANNEL_ID) -o $(RAW_DATA_DIR)/discord/$(CHANNEL_ID).csv -f Csv
