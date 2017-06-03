from random import randint

import grequests
from bs4 import BeautifulSoup
from discord.ext import commands

from src.globals import logger


class Fun:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        """
        Rolls a dice and outputs a message depending on the result
        :param ctx: The message context
        """
        random_dice = randint(1, 6)
        if random_dice < 4:
            await self.bot.say('{} rolled **{}**'.format(ctx.message.author.mention, random_dice))
        else:
            await self.bot.say(
                '{} The gods are with you, you rolled **{}**'.format(ctx.message.author.mention, random_dice))

    @commands.command(pass_context=True)
    async def randomfact(self, ctx):
        """
        Responds with a random fact scraped from unkno.com
        :param ctx: The message context
        """
        # Send typing as the request can take some time.
        await self.bot.send_typing(ctx.message.channel)

        # Build a new request object
        req = grequests.get('http://www.unkno.com/', timeout=1)
        # Send new request
        res = grequests.map([req], exception_handler=request_exception_handler)

        # res is a list of responses, since we only have one request we can just fet the first one.
        # res[0].content is the html in bytes
        soup = BeautifulSoup(res[0].content.decode(res[0].encoding), 'html.parser')
        await self.bot.say(soup.find(id='content').text)


def request_exception_handler(request, exception):
    """
    An exception handler for failed HTTP requests
    :param request: The request that failed
    :param exception: 
    """
    logger.exception('HTTP Request failed: {}'.format(request))
    logger.exception('It failed with the following exception: \n {}'.format(exception))


def setup(bot):
    bot.add_cog(Fun(bot))
