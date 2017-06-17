import sys

import discord
from discord.ext import commands
from aryas.utils import AryasFormatter, EarlyExitException

description = 'An in development python bot for the discord platform'
bot_prefix = '?'
bot = commands.Bot(command_prefix=bot_prefix, description=description, pm_help=True, formatter=AryasFormatter())
bot.remove_command('help')


# TODO: Build startup_extensions dynamically
# Config and AryasORM must be loaded first
startup_extensions = ['config', 'aryas_orm', 'general', 'modtools', 'fun', 'statistics']


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


def main():
    try:
        for extension in startup_extensions:
            extension = 'aryas.extensions.' + extension
            try:
                bot.load_extension(extension)
            except Exception as e:
                raise e

        config = bot.cogs['Config']
        bot.run(config['discord']['token'])
    except EarlyExitException as e:
        print(str(e), file=sys.stderr)
