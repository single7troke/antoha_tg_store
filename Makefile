.DEFAULT_GOAL := help
THIS_FILE := $(lastword $(MAKEFILE_LIST))
FILES := $(shell grep '^DOWNLOAD_FILES' .env | cut -f2 -d=)

help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

create_dirs:
	mkdir -p $(FILES)/1001 $(FILES)/certs $(FILES)/image
	touch $(FILES)/course_descriptor.json

generate_certs:
	openssl req -newkey rsa:2048 -sha256 -nodes -keyout $(FILES)/certs/private.key -x509 -days 3650 -out $(FILES)/certs/public.pem

run_dev:
	docker-compose -f config/dev/docker-compose.yml up --build

run_prod:
	docker-compose -f config/prod/docker-compose.yml up --build

stop_dev:
	docker-compose -f config/dev/docker-compose.yml down --remove-orphans

stop_prod:
	docker-compose -f config/prod/docker-compose.yml down --remove-orphans

restart_dev_bot:
	docker restart dev-bot-1

restart_prod_bot:
	docker restart prod-bot-1

build_dev_bot:
	docker image rm dev-bot
	docker-compose -f config/dev/docker-compose.yml build

build_prod_bot:
	docker image rm prod-bot
	docker-compose -f config/prod/docker-compose.yml build

rebuild:
	docker image rm dev-bot
	docker image rm dev-app
	docker-compose -f config/dev/docker-compose.yml build

