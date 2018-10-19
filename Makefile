.PHONY: all

all: pull deploy

pull:
	git pull

deploy:
	docker stack deploy getpet-web --compose-file docker-compose.yml
