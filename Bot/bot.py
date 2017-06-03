import discord
from discord.ext import commands

from Bot.Globals import SECRETS, extensions, status

description = 'Aryas-Bot'
bot_prefix = '?'
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


async def on_mention(message, user_mentionned):
    """
    When a mention happens, this function will be called, and handle it
    :param message:     The message that contains the mention
    :param user:        The mentionned user
    """
    if user_mentionned in status:
        await bot.send_message(message.channel, "`" + user_mentionned.name + "` is " + status[user_mentionned])


@bot.event
async def on_message(message):
    """
    When a message happens, this function is the one called
    :param message: The message that has been sent
    """
    for user in message.mentions:
        # we handle the mentions here
        await on_mention(message, user)

    await bot.process_commands(message)


def main():
    for extension in extensions:
        extension = "Commands." + extension
        try:
            bot.load_extension(extension)
        except Exception as e:
            raise e
    bot.run(SECRETS['discord']['token'])

if __name__ == "__main__":
    main()