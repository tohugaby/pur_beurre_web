#!/usr/bin/env bash

echo "Remove previous containers"
docker-compose down
echo "Remove purbeurre image"
docker rmi purbeurre:latest
echo "Build and launch containers"
docker-compose up --build -d purbeurre
echo "Set update db cron task"
ACTUAL_DIR="$(pwd)"
echo "55 23 * * 0 cd ${ACTUAL_DIR} && docker-compose up --build purbeurre_update" > purbeurre_cron
crontab purbeurre_cron
