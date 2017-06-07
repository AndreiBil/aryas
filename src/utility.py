import asyncio
from typing import Union
from discord.ext import commands
from discord import Server, Channel, Message
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


async def send(bot: commands.Bot, message: str, channel: Channel, delete=False, time=MESSAGE_SLEEP_TIME) -> None:
    """
    Sends a message to the server and deletes it after a period of time
    :param bot:     the bot used to send the message
    :param message: the content of the message
    :param channel: the channel in which the message will be sent
    :param delete: bool indicating whether to delete the message after sending it
    :param time: the time to wait before deleting the message
    """
    msg = await bot.send_message(channel, message)
    # Waits *time* seconds and deletes the confirmation message.
    if delete:
        await asyncio.sleep(time)
        await bot.delete_message(msg)
