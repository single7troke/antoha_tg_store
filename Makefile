.DEFAULT_GOAL := help
THIS_FILE := $(lastword $(MAKEFILE_LIST))
help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

run_dev:
	docker-compose -f config/dev/docker-compose.yml up

stop_dev:
	docker-compose -f config/dev/docker-compose.yml down --remove-orphans

restart_dev_bot:
	docker restart dev-bot-1

build_dev:
	docker image rm dev-bot
	docker-compose -f config/dev/docker-compose.yml buildbuild_dev:

rebuild:
	docker image rm dev-bot
	docker image rm dev-app
	docker-compose -f config/dev/docker-compose.yml build

