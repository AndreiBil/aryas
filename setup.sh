#!/usr/bin/env bash

if [[ -z "${1+present}" ]]; then
    (>&2 echo "BUILD FAILED: Please provide a Discord token.")
else
    docker build . --build-arg DISCORD_TOKEN=$1 -t aryas_bot
fi


