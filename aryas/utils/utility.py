from discord.ext import commands
import asyncio
from typing import Union
from discord import Server, Channel, Member


def is_command(bot, cmd):
    """
    Checks if the supplied string is a bot command
    :param bot: the bot
    :param cmd: the command
    :return: True if command is a bot command False otherwise
    """
    # if the string does not start with the prefix it cannot be a command
    if not cmd.startswith(bot.command_prefix):
        return False
    cmd = cmd.lstrip(bot.command_prefix).split(' ')[0]
    return cmd in bot.commands


def in_channel(name):
    """
    Checks if command is sent in a given channel
    :param name: name of the channel
    :return:
    """
    def predicate(ctx):
        return ctx.message.channel.name == name

    return commands.check(predicate)


def update_user_fields(user, member: Member):
    """
    Updates a users fields in the database with latest data from discord
    :param user: a user instance from the database
    :param member: member object from discord
    """
    user.name = member.name
    user.discriminator = member.discriminator
    user.is_bot = member.bot
    if not member.top_role.is_everyone:
        user.top_role = str(member.top_role)
    user.status = str(member.status)
    user.game = str(member.game)
    user.save()


async def kick_user(user, mod, server, bot, reason):
    """
    Kicks a user and then logs it to the 'mod_log' channel
    :param user: Member object of the user who needs to be kicked
    :param mod: Member object of the responsible moderator
    :param server: Server object of the server
    :param bot: Bot instance to kick and log 
    :param reason: Reason why user is being kicked
    """

    config = bot.cogs['Config']

    channel = get_channel_by_name(server, config['aryas']['mod_log_channel_name'])
    try:
        await bot.kick(user)
        msg = '{} was kicked by {}. Reason: {}'.format(user.name, mod.mention, reason)
        send(bot, msg, channel, False)
    except Exception as e:
        config.logger.error(e)
        send(bot, 'Failed to kick {} for {}'.format(user.mention, reason), channel, False)


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


def send(bot: commands.Bot, message: str, channel: Channel, delete=False,
         time=None, show_dots=True, bomb_themed_dots=False) -> None:
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

    config = bot.cogs['Config']
    if time is None:
        time = config['aryas']['message_sleep_time']

    def dot_bar(progress):
        width = int(time)
        if bomb_themed_dots:
            return "\n`💣" + "-" * (width - progress) + "*`" if width - progress > 0 else "💥"
        return "\n`|" + "•" * (width - progress) + " " * max(progress, 0) + "|`"

    async def send_inner():
        msg = await bot.send_message(channel, message + (dot_bar(0) if delete and show_dots else ""))
        # Waits *time* seconds and deletes the confirmation message.
        if delete:
            if not show_dots:
                await asyncio.sleep(time)
            else:
                for i in range(int(time)):
                    await asyncio.sleep(1)
                    await bot.edit_message(msg, message + dot_bar(i + 1))
            await bot.delete_message(msg)

    asyncio.ensure_future(send_inner())


async def command_error(ctx: commands.Context, msg=None, prefix=True):
    error_msg = ("Oops! That command failed!\n```\n{}\n```".format(ctx.message.clean_content) if prefix else "") + \
                ("\n" + msg if msg is not "" else "")
    await ctx.bot.send_message(ctx.message.author, error_msg)
