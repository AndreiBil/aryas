#!/usr/bin/env bash

echo && echo "=== ARYAS INSTALLER (without Docker) ==="
sudo echo > /dev/null # Get sudo permissions

echo && echo "Installing Python requirements:" \
  && sudo -H pip3 install -r ./requirements.txt | sed 's/^/    /' \
  && echo && echo "Installing Aryas:" \
  && sudo python3 ./setup.py install | sed 's/^/    /' \
  && echo && echo "Installed! Use 'aryas' to start."
