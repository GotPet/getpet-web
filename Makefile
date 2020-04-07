.PHONY: all

all: pull deploy

pull:
	git pull

deploy:
	docker stack deploy getpet-platform --with-registry-auth --compose-file docker-compose.yml

docker_push:
	 docker build -t vycius/getpet-platform  .
	 docker push vycius/getpet-platform
