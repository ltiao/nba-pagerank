#!/bin/bash

docker build -t tiao/nba-rank:api-server api
docker build -t tiao/nba-rank:frontend frontend

# docker push tiao/nba-rank:api-server
# docker push tiao/nba-rank:frontend

kubectl create -f artifacts
