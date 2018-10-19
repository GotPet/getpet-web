.PHONY: all

all: pull deploy

pull:
	git pull

deploy:
	docker-compose up -d --build
