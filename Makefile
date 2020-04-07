.PHONY: all

all: deploy

deploy:
	docker stack deploy getpet-platform --compose-file docker-compose.yml

docker_push:
	 docker build -t vycius/getpet-platform  .
	 docker push vycius/getpet-platform
