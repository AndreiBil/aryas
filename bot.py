import discord
import random
import bot
import asyncio
import json
from discord.ext import commands


description = "Aryas-Bot"
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



@bot.command(pass_context = True)
async def clear(ctx, number):
    """
    Purges messages from the channel
    :param number: The number of messages to purge
    """
    inumber = int(number)
    # Sends a deleted confirmation message
    await bot.purge_from(ctx.message.channel, limit=inumber+1)
    msg = await bot.say(number + " Messages purged")
    # Waits 3.5 seconds and deleted the confirmation message.
    await asyncio.sleep(2)
    await bot.delete_message(msg)


@bot.command(pass_context=True)
async def ping(ctx):
    await bot.say('Pong!')

bot.run(SECRETS['discord']['token'])
