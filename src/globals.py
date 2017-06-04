import json
import sqlite3
import logging

from typing import Set

conn: sqlite3.Connection = sqlite3.connect('aryas.db')

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status: Set[str] = {'away', 'vacation', 'active'}


MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'

# Setup logging.
logger: logging.Logger = logging.getLogger('discord')
