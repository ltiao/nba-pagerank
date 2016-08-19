#!/bin/bash

docker build -t tiao/nba-rank:api-server api
docker build -t tiao/nba-rank:frontend frontend
docker build -t tiao/redis-commander redis-commander

# docker push tiao/nba-rank:frontend-flask
# docker push tiao/nba-rank:frontend-nginx
# docker push tiao/redis-commander

kubectl create -f artifacts
