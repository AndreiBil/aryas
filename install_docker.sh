#!/usr/bin/env bash

echo && echo "=== ARYAS INSTALLER (with Docker) ==="
sudo echo > /dev/null # Get sudo permissions

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed! Aborting!"; exit 1; }

echo && echo "Building Docker image:" \
  && sudo docker build . -t aryas | sed 's/^/    /' \
  && echo && echo "Copying executable script to '/usr/local/bin'..." \
  && sudo cp ./bin/run_docker.sh /usr/local/bin/aryas | sed 's/^/    /' \
  && echo && echo "Installed! Use 'aryas' to start, or 'aryas -d' to start in the background."
