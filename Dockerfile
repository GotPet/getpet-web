FROM python:3.7

EXPOSE 8080

ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/platform
WORKDIR /srv/platform

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

CMD ["/bin/sh", "config/start.sh"]