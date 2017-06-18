#!/usr/bin/env bash

echo "=== ARYAS INSTALLER (without Docker) ==="
sudo echo > /dev/null # Get sudo permissions

echo "Installing Python requirements:" \
  && sudo -H pip3 install -r ./requirements.txt \
  && echo && echo "Installing Aryas:" \
  && sudo python3 ./setup.py install \
  && echo && echo "Installed! Use 'aryas' to start."
