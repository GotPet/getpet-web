.PHONY: all

all: pull deploy

pull:
	git pull

deploy:
	docker stack deploy zkr-platform --compose-file docker-compose.yml
