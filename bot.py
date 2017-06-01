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


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


@bot.command(pass_context=True)
@commands.has_role('Admin')
async def clear(ctx, number):
    """
    Purges messages from the channel
    :param ctx: The message context
    :param number: The number of messages to purge
    """
    inumber = int(number)
    if inumber <= 100:
        # Sends a deleted confirmation message
        await bot.purge_from(ctx.message.channel, limit=inumber + 1)
        msg = await bot.say(number + ' Message purged')
        # Waits 3.5 seconds and deleted the confirmation message.
        await asyncio.sleep(2)
        await bot.delete_message(msg)
    else:
        await bot.say('Cannot delete more than 100 messages at a time.')


@bot.command()
async def ping():
    await bot.say('Pong!')


@bot.command(pass_context=True)
async def show_love(ctx, mention, love):
    msg = ctx.message

    giver = ctx.message.author
    receiver = msg.raw_mentions[0]
    channel = msg.channel.id
    server = msg.server.id
    love = int(love)

    c = conn.cursor()
    c.execute("""INSERT INTO love (giver, receiver, channel, server, amount) VALUES (?, ?, ?, ?, ?)""",
              (giver.id,
               receiver,
               channel,
               server,
               love))
    conn.commit()
    await bot.say('<@{}> showed {}x❤ to {}'.format(giver.id, love, mention))


@bot.command(pass_context=True)
async def get_love(ctx, mention):
    user_id = ctx.message.raw_mentions[0]

    c = conn.cursor()
    # The comma next to user_id needs to be there, don't ask me why.
    c.execute("""SELECT SUM(amount) FROM love WHERE receiver=? """, (user_id,))
    love = c.fetchone()[0]

    if not love:
        await bot.say("<@{}> doesn't have any ❤".format(user_id, love))
    else:
        await bot.say('<@{}> has {}x❤'.format(user_id, love))


bot.run(SECRETS['discord']['token'])
