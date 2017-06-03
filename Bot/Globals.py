import json
import sqlite3

conn = sqlite3.connect('aryas.db')

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status = {'away', "vacation", "active"}
status = {}

# FIXME --> do that dynamically
# the commands
extensions = ['ping', 'clear', 'love', 'ping', 'setstatus']
