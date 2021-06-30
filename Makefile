DISCORD_CHAT_EXPORTER_DIR = "lib/discord-chat-exporter"
STANFORD_CORENLP_DIR = "lib/stanford-corenlp"
RAW_DATA_DIR := "data/raw/ext"

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

check-python-venv:
ifeq ("${VIRTUAL_ENV}","")
	$(error "You should run this in a venv")
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

clean-all: clean-data clean-logs

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

build: check-python-venv check-java-version
	@pip install -r requirements.txt
	@python build.py
	

CHANNEL_ID ?= 727433810148458498
data-scrape-discord: setup-discord-chat-exporter
	-@rm -rf $(RAW_DATA_DIR)/discord
	@mkdir -p $(RAW_DATA_DIR)/discord
	@dotnet $(DISCORD_CHAT_EXPORTER_DIR)/DiscordChatExporter.Cli.dll \
		export -t $(DISCORD_TOKEN) \
		-c $(CHANNEL_ID) -o $(RAW_DATA_DIR)/discord/$(CHANNEL_ID).csv -f Csv