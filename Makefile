.PHONY: all

all: pull deploy

pull:
	git pull

deploy:
	docker stack deploy getpet-web-platform --compose-file docker-compose.yml
