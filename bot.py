import asyncio
import json
import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('aryas.db')

description = 'Aryas-Bot'
bot_prefix = '?'

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

bot = commands.Bot(command_prefix='?', description=description)

MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'
MAX_CLEAR_NUM = 100


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


@bot.command(pass_context=True)
@commands.has_role('Admin')
async def kick(ctx, member: discord.Member, reason):
    """
    Kicks the mentioned user from the server
    :param ctx: the message context
    :param member: the member
    :param reason: the reason for the kick
    """
    try:
        discord.Client.kick(discord.Server.get_member(ctx.message.server, member))
        msg = '{} was kicked by {}. reason: {}'.format(member.name, ctx.message.author.mention, reason)
        send(msg, get_channel_by_name(ctx.message.server, MOD_LOG_CHANNEL_NAME))
    except:
        send('Failed to kick ' + member.mention, ctx.message.channel, True)


@bot.has_role('Moderator')
async def send(message, channel, delete=False, time=MESSAGE_SLEEP_TIME):
    """
    Sends a message to the server and deletes it after a period of time
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


@bot.command(pass_context=True)
@commands.has_role('Admin')
async def clear(ctx, number):
    """
    Purges messages from the channel
    :param ctx: The message context
    :param number: The number of messages to purge
    """
    inumber = int(number)
    if inumber <= MAX_CLEAR_NUM:
        # In order to delete the command message too, the number of messages to clear is incremented
        await bot.purge_from(ctx.message.channel, limit=inumber + 1)
        send(number + ' Message cleared', ctx.message.channel, True)
    else:
        send('Cannot delete more than 100 messages at a time.', ctx.message.channel, True)


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


@bot.command()
async def ping():
    await bot.say('Pong!')


@bot.command(pass_context=True)
async def show_love(ctx, member: discord.Member, love):
    """
    Gives love to a user
    :param ctx: the message context
    :param member: the member to give the love to
    :param love: the amount of love to give
    """
    msg = ctx.message
    giver = ctx.message.author
    channel = msg.channel.id
    server = msg.server.id
    love = int(love)

    c = conn.cursor()
    c.execute("""INSERT INTO love (giver, receiver, channel, server, amount) VALUES (?, ?, ?, ?, ?)""",
              (giver.id,
               member.id,
               channel,
               server,
               love))
    conn.commit()
    await bot.send('{} showed {}x❤ to {}'.format(giver.mention, love, member.mention), ctx.message.channel)


@bot.command(pass_context=True)
async def get_love(ctx, member: discord.Member):
    """
    Gives info regarding the amount of love a user has
    :param ctx: the message context
    :param member: the member
    """
    c = conn.cursor()
    # The comma next to user_id needs to be there, don't ask me why.
    c.execute("""SELECT SUM(amount) FROM love WHERE receiver=? """, (member.id,))
    love = c.fetchone()[0]

    if not love:
        await send("{} doesn't have any ❤".format(member.mention, love), ctx.message.channel)
    else:
        await send('{} has {}x❤'.format(member.mention, love), ctx.message.channel)


bot.run(SECRETS['discord']['token'])
