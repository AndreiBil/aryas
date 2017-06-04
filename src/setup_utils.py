import json
import os
import sqlite3
import sys

from jsonschema import validate

CFG_DIR = "./cfg/"
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


def create_love_table():
    """
    Creates a love table on a SQLite DB
    """
    # Create a SQLite DB and connect to it.
    conn = sqlite3.connect('aryas.db')
    c = conn.cursor()
    # Create love table
    c.execute("""CREATE TABLE IF NOT EXISTS love
                  (giver CHAR(18), receiver CHAR(18), channel CHAR(18), server CHAR(18), amount INTEGER)""")


def check_setup() -> bool:
    """
    Performs neccesary checks when starting the bot.
    :return: A boolean stating whether the program should continue.
    """
    create_love_table()
    return cfg_file_is_valid()
