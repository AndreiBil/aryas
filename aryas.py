import discord
from discord.ext import commands
import logging
from src.globals import logger
from src.globals import CFG

description = 'A in development python bot for the discord platform'
bot_prefix = '?'
bot = commands.Bot(command_prefix='?', description=description)


# Change this to get more/less logs.
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='aryas.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# TODO: Build startup_extensions dynamically
startup_extensions = ['general', 'modtools', 'fun']


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


def main():
    for extension in startup_extensions:
        extension = 'src.extensions.' + extension
        try:
            bot.load_extension(extension)
        except Exception as e:
            raise e

    bot.run(CFG['discord']['token'])
