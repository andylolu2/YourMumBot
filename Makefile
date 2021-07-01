DISCORD_CHAT_EXPORTER_DIR = "lib/discord-chat-exporter"
STANFORD_CORENLP_DIR = "lib/stanford-corenlp"
RAW_DATA_DIR := "data/raw/ext"
DOCKER_TAG := "yourmumbot:latest"
DOCKER_NAME := "yourmumbot"
DOCKER_MEM_MAX := "800m"
DOCKER_CPU_MAX := "768" # 1024 * 3 / 4
TERRAFORM_VARS := "inputVars.tfvars"

EC2_IP := $(shell cd terraform && \
	terraform output | grep -oP '(?<=instance_ip = ")[0-9\.]*(?=")')

-include .env
export

check-dotnet-version:
ifeq ($(shell dotnet --version | grep "3\.1\..*"),)
	$(error ".NET must be at version 3.1")
endif

check-java-version:	
	$(eval JAVA_VER := $(shell java --version \
		| grep -oP "[0-9]+(?=\.[0-9]+\.[0-9]+)" \
		| head -1))
	@if [ ! $(JAVA_VER) -ge 8 ]; \
		then echo "Error: at least java 8 is required"; \
	fi

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

setup-stanford-corenlp: check-java-version
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

DEV ?= False
setup: check-python-venv check-java-version
ifeq ("$(DEV)", "True")
	@pip install -r requirements.txt
	@python build.py
else 
	@pip install -r prod_requirements.txt
	@python build.py
endif	

run:
	@python -m src.main

docker-build:
	@docker build -t $(DOCKER_TAG) .

CLEAN ?= False
docker-run: docker-stop
ifeq ("$(CLEAN)", "True")
	$(eval FLAGS += "--rm")
endif
	@docker run $(FLAGS) -d --name $(DOCKER_NAME) \
		-m=$(DOCKER_MEM_MAX) -c=$(DOCKER_CPU_MAX) \
		-e DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) $(DOCKER_TAG)

docker-shell:
	@docker exec -t -i $(DOCKER_NAME) /bin/bash

docker-stats:
	@docker stats $(DOCKER_NAME)

docker-log:
	@docker logs $(DOCKER_NAME)

docker-stop:
ifneq ("$(shell docker ps -a | grep $(DOCKER_NAME))", "")
	@echo "Stopping $(DOCKER_NAME)..."
	@docker stop $(DOCKER_NAME)	
	@docker rm $(DOCKER_NAME)	
endif

docker-clean:
	@docker rmi $(DOCKER_TAG)

ssh-ec2:
	@ssh ec2-user@$(EC2_IP) $(CMD)

deploy-setup:
	@make ssh-ec2 CMD='sudo yum update -y'
	@make ssh-ec2 CMD='sudo amazon-linux-extras install docker'
	@make ssh-ec2 CMD='sudo service docker start'
	@make ssh-ec2 CMD='sudo usermod -a -G docker ec2-user'
	@make ssh-ec2 CMD='docker info'

deploy-docker:
	@docker save $(DOCKER_TAG) | bzip2 | pv | \
     ssh ec2-user@$(EC2_IP) 'bunzip2 | docker load'
	
deploy-run:
	@make ssh-ec2 CMD=\
	'docker run $(FLAGS) -d -e DISCORD_BOT_TOKEN=$(DISCORD_BOT_TOKEN) $(DOCKER_TAG)'

terraform-cmd:
	@cd terraform && terraform $(CMD)

terraform-plan:
	@make terraform-cmd CMD="plan -var-file=$(TERRAFORM_VARS)"

terraform-apply:
	@make terraform-cmd CMD="apply -var-file=$(TERRAFORM_VARS)"

terraform-%:
	@make terraform-cmd CMD="$*"

CHANNEL_ID ?= 727433810148458498
data-scrape-discord: setup-discord-chat-exporter
	-@rm -rf $(RAW_DATA_DIR)/discord
	@mkdir -p $(RAW_DATA_DIR)/discord
	@dotnet $(DISCORD_CHAT_EXPORTER_DIR)/DiscordChatExporter.Cli.dll \
		export -t $(DISCORD_TOKEN) \
		-c $(CHANNEL_ID) -o $(RAW_DATA_DIR)/discord/$(CHANNEL_ID).csv -f Csv