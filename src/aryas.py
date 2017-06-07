import discord
from discord.ext import commands


description = 'A in development python bot for the discord platform'
bot_prefix = '?'
bot = commands.Bot(command_prefix='?', description=description, pm_help=True, help_attrs=dict(hidden=True))

# TODO: Build startup_extensions dynamically
# Config and AryasORM must be loaded first
startup_extensions = ['config', 'aryasorm', 'general', 'modtools', 'fun']


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

    config = bot.cogs['Config']
    bot.run(config['discord']['token'])
