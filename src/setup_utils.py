import json
import os
import sys

from jsonschema import validate

CFG_DIR = './.aryas/'
FILENAME = 'cfg.json'

DEFAULT_CFG = {
    'aryas': {
        'env': 'dev',
        'log_level': 'DEBUG',
        'message_sleep_time': 2,
        'mod_log_channel_name': 'mod_log',
        'db': {
            'name': 'aryas'
        }
    },
    'discord': {
        'token': ''
    },
    'weather': {
        'api_key': ''
    }
}

CFG_SCHEMA = {
    'type': 'object',
    'properties': {
        'aryas': {
            'type': 'object',
            'properties': {
                'env': {'type': 'string'},
                'log_level': {'type': 'string'},
                'message_sleep_time': {'type': 'integer'},
                'mod_log_channel_name': {'type': 'string'},
                'db': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'provider': {'type': 'string'},
                        'host': {'type': 'string'},
                        'user': {'type': 'string'},
                        'pass': {'type': 'string'}
                    }
                }
            }
        },
        'discord': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string'}
            },
            'required': ['token']
        },
        'weather': {
            'type': 'object',
            'properties': {
                'api_key': {'type': 'string'}
            },
            'required': ['api_key']
        }
    },
    'required': ['discord', 'weather']
}


def cfg_file_is_valid() -> bool:
    """
    Validates secrets.json file.
    :returns: A boolean of whether the cfg file is valid.
    """
    if not os.path.isdir(CFG_DIR):
        os.mkdir(CFG_DIR)

    try:
        with open(CFG_DIR+FILENAME, 'r') as f:
            data = json.load(f)
            validate(data, CFG_SCHEMA)
            return True
    except FileNotFoundError:
        print('cfg.json does not exist!', file=sys.stderr)
        with open(CFG_DIR+FILENAME, 'w') as f:
            json.dump(DEFAULT_CFG, f, indent=2, separators=(',', ': '))
        print('Please enter necessary info into {}{} and try again.'.format(CFG_DIR, FILENAME), file=sys.stderr)

    return False


def check_setup() -> bool:
    """
    Performs neccesary checks when starting the bot.
    :return: A boolean stating whether the program should continue.
    """
    return cfg_file_is_valid()
