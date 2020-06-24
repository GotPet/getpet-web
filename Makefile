.PHONY: all

all: deploy

deploy:
	docker stack deploy getpet-platform --compose-file docker-compose.yml

nginx_reload:
	docker exec $(docker ps -aqf "label=lt.getpet.nginx") nginx -s reload

docker_push:
	 docker build --build-arg=GIT_COMMIT=$(git rev-parse --short HEAD) --build-arg=GIT_BRANCH=$SOURCE_BRANCH -t vycius/getpet-platform  .
	 docker push vycius/getpet-platform
