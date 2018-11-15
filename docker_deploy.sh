#!/usr/bin/env bash

echo "Remove previous containers"
docker-compose down
echo "Remove purbeurre image"
docker rmi pur_beurre_web_purbeurre:latest
echo "Build and launch containers"
docker-compose up -d
