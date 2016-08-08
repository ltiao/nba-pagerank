#!/bin/bash

docker build -t tiao/nba-rank:frontend-flask frontend/flask
docker build -t tiao/nba-rank:frontend-nginx frontend/nginx
docker build -t tiao/redis-commander redis-commander

# docker push tiao/nba-rank:frontend-uwsgi 
# docker push tiao/nba-rank:frontend-nginx 

kubectl create -f artifacts
