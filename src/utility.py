import asyncio
from typing import Union

from discord import Server, Channel
from discord.ext import commands

from src.globals import MESSAGE_SLEEP_TIME, logger, MOD_LOG_CHANNEL_NAME


async def kick_user(user, mod, server, bot, reason):
    """
    Kicks a user and then logs it to the 'mod_log' channel
    :param user: Member object of the user who needs to be kicked
    :param mod: Member object of the responsible moderator
    :param server: Server object of the server
    :param bot: Bot instance to kick and log 
    :param reason: Reason why user is being kicked
    """
    channel = get_channel_by_name(server, MOD_LOG_CHANNEL_NAME)
    try:
        await bot.kick(user)
        msg = '{} was kicked by {}. Reason: {}'.format(user.name, mod.mention, reason)
        await send(bot, msg, channel, False)
    except Exception as e:
        logger.error(e)
        await send(bot, 'Failed to kick {} for {}'.format(user.mention, reason), channel, False)


def get_channel_by_name(server: Server, name: str) -> Union[Channel, None]:
    """
    Finds a channel by it's name and returns it's channel object
    :param server: the server where the channel is in
    :param name: the name of the channel
    :return: channel object if channel was found, otherwise None
    """
    for channel in server.channels:
        if channel.name == name:
            return channel
    return None


async def send(bot: commands.Bot, message: str, channel: Channel, delete=False, time=MESSAGE_SLEEP_TIME,
               show_dots=True, bomb_themed_dots=False) -> None:
    """
    Sends a message to the server and deletes it after a period of time
    :param bot:     the bot used to send the message
    :param message: the content of the message
    :param channel: the channel in which the message will be sent
    :param delete: whether to delete the message after sending it
    :param time: the time to wait before deleting the message
    :param show_dots: whether to show countdown dots for message deletion (this will round down `time` if it is a float)
    :param bomb_themed_dots: whether to theme the dots using a bomb and fuse instead of plain dots
    """

    def dot_bar(width, progress):
        if bomb_themed_dots:
            return "\n`💣" + "-"*(width-progress) + "*`" if width-progress > 0 else "💥"
        return "\n`" + "."*(width-progress) + " `"

    msg = await bot.send_message(channel, message + (dot_bar(int(time), 0) if show_dots else ""))
    # Waits *time* seconds and deletes the confirmation message.
    if delete:
        if not show_dots:
            await asyncio.sleep(time)
        else:
            for i in range(time):
                await asyncio.sleep(1)
                await bot.edit_message(msg, message+dot_bar(int(time), i+1))
        await bot.delete_message(msg)

async def command_error(ctx: commands.Context, msg=None, prefix=True):
    error_msg = ("Oops! That command failed!\n```\n{}\n```".format(ctx.message.content) if prefix else "") + \
                ("\n"+msg if msg is not "" else "")
    await ctx.bot.send_message(ctx.message.author, error_msg)
