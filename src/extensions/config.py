"""
A special config extension. This extension does not hold any bot commands or events, but is used to load the config file
to be used throughout the bot. All values in `cfg.json` can be accessed with standard dictionary, additional property
methods are also available. Database variables should be accessed through the `db` property.
"""
import json
import logging
from typing import Dict, Set, Tuple

import yaml
from cerberus import Validator
from discord.ext import commands
from peewee import Proxy


class _Constants:
    def __init__(self):
        default = self.default_config
        self._config_schema = {
            "aryas": {"type": "dict", "required": True, "default": default["aryas"], "schema": {
                "db": {"type": "dict", "required": True, "default": default["aryas"]["db"], "schema": {
                    "host": {"type": "string", "required": True, "default": default["aryas"]["db"]["host"]},
                    "name": {"type": "string", "required": True, "default": default["aryas"]["db"]["name"]},
                    "user": {"type": "string", "required": True, "default": default["aryas"]["db"]["user"]},
                    "pass": {"type": "string", "required": True, "default": default["aryas"]["db"]["pass"]}
                }},
                "env": {"type": "string", "required": False, "default": default["aryas"]["env"],
                        "allowed": ("prod", "dev")},
                "log_level": {"type": ["string", "integer"], "required": False,
                              "default": default["aryas"]["log_level"], "allowed": self.possible_log_levels}
            }},
            "discord": {"type": "dict", "required": True, "default": default["discord"], "schema": {
                "token": {"type": "string", "required": True, "default": default["discord"]["token"]}
            }},
            "weather": {"type": "dict", "required": False, "default": default["weather"], "schema": {
                "api_key": {"type": "string", "required": False, "default": default["weather"]["api_key"]}
            }}
        }

    @property
    def rules(self) -> str:
        return """1. Be polite.
2. Respect the opinion of others. ( Apple < Android  tho and fuck anyone who says otherwise)
3. Don't spam.
4. Try Google before you ask questions here
5. Don't advertise any other discord server in any of the channels/DMs unless given permission by a mod/admin.
6. Use the appropriate channels for your question.
7. Don't have anything relevant to add in the programming channels? Stay quiet :smiley: :kissing_heart: 
8. Don't post any NSFW content.
9.  Use your common sense ¯\_(ツ)_/¯
10. Don't ask people for help in PMs. Use the designated channels instead.

11. But most importantly, HAVE FUN! That's so corny and cringy but I had to add that for the lulz

**Code formatting**
\```python
def your_awesome_func():
    return 1+1
\```
will produce
```python
def your_awesome_func():
    return 1+1
```"""

    @property
    def len_units(self) -> Dict[str, float]:
        return {'millimeter': 0.001, 'mm': 0.001, 'centimeter': 0.01, 'cm': 0.01, 'meter': 1, 'm': 1,
                'kilometer': 1000,
                'km': 1000, 'inch': 0.0254, 'in': 0.0254, 'foot': 3.28084, 'ft': 3.28084, 'yard': 1.09361}

    @property
    def mass_units(self) -> Dict[str, float]:
        return {'milligram': 0.000001, 'mg': 0.000001, 'gram': 0.001, 'g': 0.001, 'kilogram': 1, 'kg': 1,
                'ton': 1000,
                'pound': 0.453592, 'ounce': 0.0283495}

    @property
    def possible_status(self) -> Set[str]:
        return {'away', 'vacation', 'active'}

    @property
    def embed_color(self) -> int:
        return 0xff80ff

    @property
    def possible_log_levels(self) -> Tuple:
        return "CRITICAL", 50, \
               "ERROR", 40, \
               "WARNING", 30, \
               "INFO", 20, \
               "DEBUG", 10, \
               "NOTSET", 0

    @property
    def default_config(self) -> dict:
        return {
            "aryas": {
                "db": {
                    "host": "127.0.0.1",
                    "name": "",
                    "user": "",
                    "pass": ""
                },
                "env": "prod",
                "log_level": 0
            },
            "discord": {
                "token": ""
            },
            "weather": {
                "api_key": ""
            }
        }

    @property
    def config_schema(self) -> dict:
        return self._config_schema

    @property
    def cache_dir(self) -> str:
        return "./.aryas/"

    @property
    def cfg_file(self) -> str:
        return self.cache_dir + "cfg.json"

    @property
    def message_sleep_time(self) -> int:
        return 2


class Config:
    def __init__(self):
        self._constants = _Constants()

        self._config_dict = self._parse_config()

        self._log = logging.getLogger('discord')

    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        return self._config_dict[item]

    @property
    def logger(self):
        """
        Setups up the logger object to be used throughout the bot.
        This potentially belongs in its own extension.
        """
        # Change this to get more/less logs.
        self._log.setLevel(self['aryas']['log_level'])
        handler = logging.FileHandler(filename=self.constants.cache_dir + 'aryas.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self._log.addHandler(handler)
        return self._log

    @property
    def db(self) -> dict:
        """
        Sets up the database proxy and exposes the database variables in a `db` property.
        """
        # Create a database proxy (placeholder) to be filled at runtime with the actual database object.
        self._config_dict['aryas']['db']['_db_proxy'] = Proxy()
        return self._config_dict['aryas']['db']

    @property
    def env(self):
        return self._config_dict['aryas']['env']

    @property
    def constants(self) -> _Constants:
        return self._constants

    def _parse_config(self) -> dict:
        """
        Parses configuration from the config file, checked against _Constants.cfg_schema.
        This will throw an exception if the config is invalid.
        After checking, default values will be inserted and the config saved, *whether it was found valid or not*.
        :return: The config dict
        """

        class ConfigParseException(Exception):
            pass

        v = Validator(self.constants.config_schema)
        with open(self.constants.cfg_file, "r") as f:
            loaded = json.load(f)
        try:
            if not v.validate(loaded):
                print(v.errors, type(v.errors))
                raise ConfigParseException("There were errors with your config!\n" + yaml.dump(v.errors, indent=2))
        finally:
            normalized = v.normalized(loaded)  # Insert default values for missing keys
            with open(self.constants.cfg_file, "w") as f:
                json.dump(normalized, f, indent=2)

        return normalized


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Config())
