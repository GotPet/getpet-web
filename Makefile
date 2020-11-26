.PHONY: all

all: deploy

deploy:
	docker stack deploy getpet-platform --with-registry-auth --compose-file docker-compose.yml

nginx_reload:
	docker exec $(docker ps -qf "label=lt.getpet.nginx") nginx -s reload

python_shell:
	docker exec -it $(docker ps -qf "label=lt.getpet.platform" | head -n 1) python manage.py shell

docker_push:
	 docker build --build-arg=GIT_COMMIT=$(git rev-parse --short HEAD) --build-arg=GIT_BRANCH=$SOURCE_BRANCH -t vycius/getpet-platform  .
	 docker push vycius/getpet-platform
