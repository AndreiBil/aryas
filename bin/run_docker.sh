#!/usr/bin/env bash

while getopts ":d" opt; do
  case ${opt} in
    d)
      echo "Starting Aryas in the background..."
      docker run -rm -d --restart always --net=host --name aryas_bot -v ~/.aryas:/root/.aryas aryas_bot
      exit
      ;;
  esac
done

echo "Starting Aryas..."
docker run -rm -t --net=host --name aryas_bot -v ~/.aryas:/root/.aryas aryas_bot
