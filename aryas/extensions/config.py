"""
A special config extension. This extension does not hold any bot commands or events, but is used to load the config file
to be used throughout the bot. All values in `cfg.json` can be accessed with standard dictionary, additional property
methods are also available. Database variables should be accessed through the `db` property.
"""
import os

import json
import logging
import shelve
from datetime import datetime
from typing import Set, Tuple, Dict, Callable

from cerberus import Validator
from discord.ext import commands
from peewee import Proxy

from ..exceptions import EarlyExitException


class _Constants:
    def __init__(self, config):
        self._config = config

        default = self.default_config
        self._config_schema = {
            'aryas': {'type': 'dict', 'required': True, 'default': default['aryas'], 'schema': {
                'db': {'type': 'dict', 'required': True, 'default': default['aryas']['db'], 'schema': {
                    'host': {'type': 'string', 'required': True, 'default': default['aryas']['db']['host']},
                    'name': {'type': 'string', 'required': False, 'default': default['aryas']['db']['name']},
                    'user': {'type': 'string', 'required': True, 'default': default['aryas']['db']['user']},
                    'pass': {'type': 'string', 'required': True, 'default': default['aryas']['db']['pass']}
                }},
                'env': {'type': 'string', 'required': False, 'default': default['aryas']['env'],
                        'allowed': ('prod', 'dev')},
                'log_level': {'type': ['string', 'integer'], 'required': False,
                              'default': default['aryas']['log_level'], 'allowed': self.possible_log_levels},
                'message_sleep_time': {'type': 'number', 'required': True,
                                       'default': default['aryas']['message_sleep_time']},
                'mod_log_channel_name': {'type': 'string', 'required': True, 'empty': False}
            }},
            'discord': {'type': 'dict', 'required': True, 'default': default['discord'], 'schema': {
                'token': {'type': 'string', 'required': True, 'default': default['discord']['token'], 'empty': False}
            }},
            'weather': {'type': 'dict', 'required': False, 'default': default['weather'], 'schema': {
                'api_key': {'type': 'string', 'required': False, 'default': default['weather']['api_key']}
            }},
            'google': {'type': 'dict', 'required': False, 'default': default['google'], 'schema': {
                'api_key': {'type': 'string', 'required': False, 'default': default['google']['api_key']},
                'cse_name': {'type': 'string', 'required': False, 'default': default['google']['cse_name']},
                'cse_id': {'type': 'string', 'required': False, 'default': default['google']['cse_id']}
            }}
        }

    @property
    def rules_general(self) -> str:
        return ("1. NSFW is not allowed, keep the chat racism free, clean, polite!\n"
                "2. There are moments when you won't agree with other users. Keep it civil, agree to disagree!\n"
                "3. Don't spam.\n"
                "4. Try to solve your problem through Google and Stack Overflow before you ask your questions here\n"
                "5. Don't advertise any other discord server in any of the channels/DMs unless given permission "
                "by a mod/admin.")

    @property
    def rules_channels(self) -> str:
        return ("1. Use the appropriate channels for your question.\n"
                "2. Don't have anything relevant to add in the programming channels? Stay quiet!\n"
                "3. *#general* chat is for socializing with other peers, talk about life, parties, health, "
                "jobs and others, try to keep the topics serious , for rest use *#offtopic_chat*\n"
                "4. We have a channel for off-topic discussions, the channel is *#offtopic_chat* , use that for ex: "
                "fidget spinners discussions, iphone vs samsung discussions, etc\n"
                "5. Don't ask people for help in PMs. Use the designated channels instead.\n"
                "6. *#show_your_project* is a place where you can showplace your project; "
                "it must be hosted on github to be approved.")

    @property
    def rules_roles(self) -> str:
        return ("1. **Trusted** role is given to people who are active in the community --> "
                "Trusted role allows you to post links and images. To receive this role you need to PM a moderator\n"
                "2. **Support** role is given to people who are active in the community and who help other people "
                "who are in need of help --> To achieve this role there are 2 ways, either people will recommend you "
                "or you can ask for it and if you are worthy, you will receive it .\n"
                "3. Language roles are given for now to support role only , in the future this might change!")

    @property
    def rules_code_formatting(self) -> str:
        return """Discord has support for source code highlighting by doing
\```python
def your_awesome_func():
    return 1+1
\```
you will get
```python
def your_awesome_func():
    return 1+1
```

But most importantly, HAVE FUN! If problems arise contact a moderator"""

    @property
    def possible_status(self) -> Set[str]:
        return {'away', 'vacation', 'active'}

    @property
    def embed_color(self) -> int:
        return 0x50A6C2

    @property
    def possible_log_levels(self) -> Tuple:
        return 'CRITICAL', 50, \
               'ERROR', 40, \
               'WARNING', 30, \
               'INFO', 20, \
               'DEBUG', 10, \
               'NOTSET', 0

    @property
    def default_config(self) -> dict:
        return {
            'aryas': {
                'db': {
                    'host': '127.0.0.1',
                    'name': 'aryas',
                    'user': '',
                    'pass': ''
                },
                'env': 'prod',
                'log_level': 0,
                'message_sleep_time': 2,
                'mod_log_channel_name': 'mod_log'
            },
            'discord': {
                'token': ''
            },
            'weather': {
                'api_key': ''
            },
            'google': {
                'api_key': '',
                'cse_name': '',
                'cse_id': ''
            }
        }

    @property
    def config_schema(self) -> dict:
        return self._config_schema

    @property
    def vars_defaults(self) -> Dict[str, Callable]:

        # Vars schema guide:
        #   'var_name': <supplier function for default value>
        # If your default value is constant, just use lambda: myVal

        return {
            'last_love_reset': datetime.now
        }

    @property
    def cache_dir_raw(self) -> str:
        return '~/.aryas/'

    @property
    def cache_dir(self) -> str:
        return os.path.expanduser(self.cache_dir_raw.replace("/", os.sep))

    @property
    def cfg_file(self) -> str:
        return self.cache_dir + 'cfg.json'

    @property
    def vars_file(self):
        return self.cache_dir + 'vars.data'

    @property
    def env(self):
        return self._config['aryas']['env']


class Vars:
    def __init__(self, cfg: Config):
        self._vars: dict = dict()
        self._cfg: Config = cfg
        self._check_defaults()

    def _open_shelf(self, flag):
        if flag not in 'wrc':
            raise ValueError('shelf flag must be \'w\', \'r\' or \'c\'')
        return shelve.open(self._cfg.constants.vars_file, flag)

    def __getitem__(self, item):
        with self._open_shelf('r') as shelf:
            return shelf[item]

    def __setitem__(self, key, value):
        with self._open_shelf('w') as shelf:
            shelf[key] = value

    def _check_defaults(self):
        with self._open_shelf('c') as shelf:
            for var_name, default_val_supplier in self._cfg.constants.vars_defaults.items():
                if var_name not in shelf:
                    shelf[var_name] = default_val_supplier()


class Config:
    def __init__(self):
        self._constants = _Constants(self)

        self._vars = Vars(self)

        self._config_dict = self._parse_config()

        self._log = logging.getLogger('discord')

    def __getitem__(self, item):
        """

        :param item:
        :return:
        """
        return self._config_dict[item]

    @property
    def vars(self) -> Vars:
        return self._vars

    @property
    def logger(self) -> logging.Logger:
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
    def constants(self) -> _Constants:
        return self._constants

    def _parse_config(self) -> dict:
        """
        Parses configuration from the config file, checked against _Constants.cfg_schema.
        This will throw an exception if the config is invalid.
        After checking, default values will be inserted and the config saved, *whether it was found valid or not*.
        :return: The config dict
        """

        v = Validator(self.constants.config_schema)
        loaded = None
        try:
            with open(self.constants.cfg_file, 'r') as f:
                loaded = json.load(f)

            if not v.validate(loaded):
                with open(self.constants.cache_dir + "cfg_errors.json", "w") as f:
                    json.dump(v.errors, f, indent=2)
                raise EarlyExitException('There were errors with your config!\n'
                                         'Error details were dumped to cfg_errors.json')
        except FileNotFoundError:
            if not os.path.isdir(self.constants.cache_dir):
                os.mkdir(self.constants.cache_dir)
            raise EarlyExitException("Config file doesnt exist! Default config generated at " + self.constants.cfg_file)
        finally:
            normalized = v.normalized(loaded) \
                if loaded is not None else self.constants.default_config  # Insert default values for missing keys
            with open(self.constants.cfg_file, 'w') as f:
                json.dump(normalized, f, indent=2)

        return normalized


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Config())
