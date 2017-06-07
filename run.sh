#!/usr/bin/env bash

docker run -d --restart always --net=host --name aryas_bot -v ~/.aryas:/root/.aryas aryas_bot

