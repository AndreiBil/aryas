import asyncio

from discord.ext import commands

from Bot.Globals import MESSAGE_SLEEP_TIME


def get_channel_by_name(server, name):
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


@commands.has_role('Moderator')
async def send(bot, message, channel, delete=False, time=MESSAGE_SLEEP_TIME):
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
