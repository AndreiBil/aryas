import discord
from discord.ext import commands

from src.globals import SECRETS

description = 'Aryas-Bot'
bot_prefix = '?'
bot = commands.Bot(command_prefix='?', description=description)

# TODO: Build startup_extensions dynamically
startup_extensions = ['general', 'survey', 'modtools']


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


if __name__ == "__main__":
    for extension in startup_extensions:
        extension = 'src.extensions.' + extension
        try:
            bot.load_extension(extension)
        except Exception as e:
            raise e

    bot.run(SECRETS['discord']['token'])