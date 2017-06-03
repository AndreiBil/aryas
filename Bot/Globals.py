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
extensions = ['ping', 'clear', 'love', 'setstatus', 'survey', 'kick', 'roll']

MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'
MAX_CLEAR_NUM = 100
