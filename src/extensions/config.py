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

    @property
    def rules(self):
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
    def len_units(self):
        return {'millimeter': 0.001, 'mm': 0.001, 'centimeter': 0.01, 'cm': 0.01, 'meter': 1, 'm': 1, 'kilometer': 1000,
                'km': 1000, 'inch': 0.0254, 'in': 0.0254, 'foot': 3.28084, 'ft': 3.28084, 'yard': 1.09361}

    @property
    def mass_units(self):
        return {'milligram': 0.000001, 'mg': 0.000001, 'gram': 0.001, 'g': 0.001, 'kilogram': 1, 'kg': 1, 'ton': 1000,
                'pound': 0.453592, 'ounce': 0.0283495}
    
    @property
    def possible_status(self):
        return {'away', 'vacation', 'active'}
    
    @property
    def embed_color(self):
        return 0xff80ff


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Config())
