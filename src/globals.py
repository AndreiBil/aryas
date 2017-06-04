import json
import logging
from peewee import MySQLDatabase

# Temporarily stored as a global. In the future this will change depending on the environment
DATABASE = MySQLDatabase(database='aryas', user='root', password='')

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status = {'away', 'vacation', 'active'}


MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'

# Setup logging.
logger = logging.getLogger('discord')
