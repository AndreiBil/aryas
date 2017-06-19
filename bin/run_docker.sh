#!/usr/bin/env bash

while getopts ":d" opt; do
  case ${opt} in
    d)
      echo "Starting Aryas in the background..."
      docker run -d --restart always --net=host --name aryas -v ~/.aryas:/root/.aryas aryas
      exit
      ;;
  esac
done

echo "Starting Aryas..."
docker run --rm -it --net=host --name aryas -v ~/.aryas:/root/.aryas aryas
