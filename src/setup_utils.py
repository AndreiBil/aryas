import json
import os
import sqlite3
import sys

from jsonschema import validate

CFG_DIR = "./.aryas/"
FILENAME = "cfg.json"

DEFAULT_CFG = {
    'discord': {
        'token': ''
    },
    'weather': {
        'api_key': ''
    }
}

CFG_SCHEMA = {
    "type": "object",
    "properties": {
        "discord": {
            "type": "object",
            "properties": {
                "token": {"type": "string"}
            },
            "required": ["token"]
        },
        "weather": {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"}
            },
            "required": ["api_key"]
        }
    },
    "required": ["discord", "weather"]
}


def cfg_file_is_valid() -> bool:
    """
    Validates secrets.json file.
    :returns: A boolean of whether the cfg file is valid.
    """
    if not os.path.isdir(CFG_DIR):
        os.mkdir(CFG_DIR)

    try:
        with open(CFG_DIR+FILENAME, "r") as f:
            data = json.load(f)
            validate(data, CFG_SCHEMA)
            return True
    except FileNotFoundError:
        print("cfg.json does not exist!", file=sys.stderr)
        with open(CFG_DIR+FILENAME, "w") as f:
            json.dump(DEFAULT_CFG, f, indent=2, separators=(',', ': '))
        print("Please enter necessary info and try again.", file=sys.stderr)

    return False


def check_setup() -> bool:
    """
    Performs neccesary checks when starting the bot.
    :return: A boolean stating whether the program should continue.
    """
    return cfg_file_is_valid()
