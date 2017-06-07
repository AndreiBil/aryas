"""
A special config extension. This extension does not hold any bot commands or events, but is used to load the config file
to be used throughout the bot. All values in `cfg.json` can be accessed with standard dictionary, additional property
methods are also available. Database variables should be accessed through the `db` property.
"""
from peewee import Proxy
from discord.ext import commands
import json
import logging


class Config:
    def __init__(self):
        self.cache_dir = './.aryas/'
        with open(self.cache_dir + 'cfg.json') as data_file:
            self._config_dict = json.load(data_file)

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
        self._log.setLevel(self._config_dict['aryas']['log_level'])
        handler = logging.FileHandler(filename=self.cache_dir + 'aryas.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self._log.addHandler(handler)
        return self._log

    @property
    def db(self) -> dict:
        """
        Sets up the database proxy and exposes the database variables in a `db` property. 
        """
        # Create a database proxy (placeholder) to be filled at runtime with the actual database object.
        self._config_dict['aryas']['db']['database_proxy'] = Proxy()
        return self._config_dict['aryas']['db']

    @property
    def env(self):
        return self._config_dict['aryas']['env']


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Config())
