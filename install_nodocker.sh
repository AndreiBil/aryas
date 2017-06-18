#!/usr/bin/env bash

echo "=== ARYAS INSTALLER (without Docker) ==="
sudo echo > /dev/null # Get sudo permissions

echo "Installing Python requirements:" \
  && sudo -H pip3 install -r ./requirements.txt \
  && echo "\nInstalling Aryas:" \
  && sudo python3 ./setup.py install \
  && echo "\nInstalled! Use 'aryas' to start."
