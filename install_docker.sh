#!/usr/bin/env bash

echo "=== ARYAS INSTALLER (with Docker) ==="
sudo echo > /dev/null # Get sudo permissions

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed! Aborting!"; exit 1; }

sudo docker build . -t aryas \
  && sudo cp ./bin/docker_run.sh /usr/local/bin/aryas \
  && echo "\nInstalled! Use 'aryas' to start, or 'aryas -d' to start in the background."
