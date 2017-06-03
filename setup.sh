#!/usr/bin/env bash

if [[ -z "${2+present}" ]]; then
    (>&2 echo "BUILD FAILED: Please provide a Discord token and weater API key.")
else
    docker build . --build-arg DISCORD_TOKEN=$1 --build-arg WEATHER_KEY=$2 -t aryas_bot
fi


