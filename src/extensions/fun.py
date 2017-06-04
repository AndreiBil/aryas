from asyncio import sleep
from random import randint

import discord
import requests
import grequests
from bs4 import BeautifulSoup
from discord.ext import commands
from typing import List, Tuple

from src.globals import logger


class Fun:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(pass_context=True)
    async def roll(self, ctx: commands.Context) -> None:
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
    async def telljoke(self, ctx: commands.Context) -> None:
        """
        Responds with a random joke from theoatmeal.com
        :param ctx: The message context
        """
        # TODO: get more joke formats (or a better source)
        # Send typing as the request can take some time.
        await self.bot.send_typing(ctx.message.channel)

        # Build a new request object
        req: grequests.AsyncRequest = grequests.get('http://theoatmeal.com/djtaf/', timeout=1)
        # Send new request
        res: List[requests.Response] = grequests.map([req], exception_handler=request_exception_handler)

        # Since we only have one request we can just fetch the first one.
        # res[0].content is the html in bytes
        soup = BeautifulSoup(res[0].content.decode(res[0].encoding), 'html.parser')
        joke_ul = soup.find(id='joke_0')
        joke = joke_ul.find('h2', {'class': 'part1'}).text.lstrip() + '\n' + joke_ul.find(id='part2_0').text
        await self.bot.say(joke)

    @commands.command(pass_context=True)
    async def randomfact(self, ctx: commands.Context) -> None:
        """
        Responds with a random fact scraped from unkno.com
        :param ctx: The message context
        """
        # Send typing as the request can take some time.
        await self.bot.send_typing(ctx.message.channel)

        # Build a new request object
        req: grequests.AsyncRequest = grequests.get('http://www.unkno.com/', timeout=1)
        # Send new request
        res: List[requests.Response] = grequests.map([req], exception_handler=request_exception_handler)

        # Since we only have one request we can just fetch the first one.
        # res[0].content is the html in bytes
        soup = BeautifulSoup(res[0].content.decode(res[0].encoding), 'html.parser')
        await self.bot.say(soup.find(id='content').text)

    @commands.command(pass_context=True)
    @commands.has_role('Moderator')
    async def poll(self, ctx: commands.Context) -> None:
        """
        Creates an interactive poll for the moderators
            The format to ask a question is :
                               '?survey <question here> ? <survey 1> - <survey 2> - ... ! <nb of minutes for timeout>')
        :param ctx:     The context of the message (cf discord doc)
        """

        usage = "?poll <question>; <length in seconds>; <option 1>; <option 2>; ..."

        # <editor-fold desc="Helper Functions and Classes">

        class PollParseException(RuntimeError):
            pass

        def format_poll_prompt(question_, options_: Tuple[str, ...]) -> str:
            """
            :param question_:    The question to ask
            :param options_:    The possible answers
            :return:    The poll prompt, eg:
                    A. Argument 1
                    B. Argument 2
                    etc.
            """

            return "__**" + question_ + "**__\n" + \
                   ("\n".join([
                       "\t" + chr(ord('A') + i) + ".\t " + arg
                       for i, arg in enumerate(options_)
                   ]))

        def get_answer_emojis(num: int) -> List[str]:
            return [chr(0x0001f1e6 + x) for x in range(num)]

        def parse_poll(message) -> Tuple[str, float, Tuple[str, ...]]:
            # "?poll "
            message = message[6:]  # Take out "?poll "
            args = tuple(map(lambda arg: arg.strip(), message.split(";")))  # Split args by ";" and trim whitespace
            if len(args) < 4:
                raise PollParseException("At least 4 args must be supplied; {} given!".format(len(args)))

            question_ = args[0]  # First arg is the question

            try:
                timeout_ = float(args[1])*60  # Second arg is the timeout, in minutes (now converted to seconds)
                if timeout_ < 0:
                    raise ValueError()
            except ValueError:
                raise PollParseException("Timeout must be a positive number; `{}` given!".format(args[1]))

            options_ = args[2:]
            if len(options_) > 25:
                raise PollParseException("Too many options; at most 25 should be given, {} actually given!"
                                         .format(len(options_)))

            return question_, timeout_, options_

        # </editor-fold>

        try:
            question, timeout, options = parse_poll(ctx.message.content)
        except PollParseException as e:
            await self.bot.say(str(e) + "\nCorrect usage: `{}`".format(usage))
            return

        await self.bot.delete_message(ctx.message)  # Delete the command message to avoid redundancy.

        #  Send the poll prompt
        em = discord.Embed(title="{}'s poll".format(ctx.message.author.name),
                           description=format_poll_prompt(question, options),
                           colour=discord.Colour.blue())

        answer_emojis = get_answer_emojis(len(options))

        msg: discord.Message = await self.bot.say("", embed=em)

        to_delete = await self.bot.say("*Setting up poll; please wait...*")
        for emoji in answer_emojis:  # Add possible answer emojis
            await self.bot.add_reaction(msg, emoji)
        await self.bot.delete_message(to_delete)

        await sleep(timeout)

        totals: List[int] = [0 for _ in range(len(answer_emojis))]
        # TODO: Check whether the `Message` object auto-updates
        updated_msg = await self.bot.get_message(channel=msg.channel, id=msg.id)
        for reaction in updated_msg.reactions:  # type: discord.Reaction
            if reaction.emoji in answer_emojis:
                totals[answer_emojis.index(reaction.emoji)] = reaction.count - 1

        author = ctx.message.author.name
        results_title = "__**Results of {} poll:**__\n" \
            .format(author + "'" + ("" if author.lower().endswith("s") else "s"))
        results_desc = "\n".join(["{} -> {}".format(answer, total) for answer, total in zip(options, totals)])

        # TODO: Draw and post a graph of the results.
        em = discord.Embed(title=results_title, description=results_desc, colour=discord.Colour.dark_green())
        await self.bot.say('', embed=em)


def request_exception_handler(request, exception) -> None:
    """
    An exception handler for failed HTTP requests
    :param request: The request that failed
    :param exception: 
    """
    logger.exception('HTTP Request failed: {}'.format(request))
    logger.exception('It failed with the following exception: \n {}'.format(exception))


def setup(bot) -> None:
    bot.add_cog(Fun(bot))
