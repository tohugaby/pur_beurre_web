#!/usr/bin/env bash

echo "Remove previous containers"
docker-compose down
echo "Remove purbeurre image"
docker rmi purbeurreweb_purbeurre:latest
echo "Build and launch containers"
pwd
docker-compose up -d
