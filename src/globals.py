import json
import logging
from src.db import Database


with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status = {'away', 'vacation', 'active'}


MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'

# Setup logging.
logger = logging.getLogger('discord')
