import json
import sqlite3
import logging

conn = sqlite3.connect('aryas.db')

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status = {'away', 'vacation', 'active'}


MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'
WEATHER_API_KEY = '91bfa6f38476eca3508edd2a0fb98b9c'

# Setup logging.
logger = logging.getLogger('discord')