import discord
import pyowm
from discord.ext import commands
from src.globals import CFG, conn, logger, RULES, LEN_UNITS, MASS_UNITS

from src.utility import send
from urllib import request
import json

import time


class General:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def on_member_join(self, member: discord.Member):
        """
        Sends a private message to new users with welcome information
        :param member: the member
        """
        # Create embed
        title = 'Welcome to Developers'
        desc = 'Stuff that happens here'
        message = discord.Embed(title=title, description=desc, color=0xff80ff)
        message.add_field(name='Rules', value=RULES, inline=False)
        message.set_footer(text='I am a bot BEEP BOOP')

        await self.bot.send_message(member, embed=message)

    @commands.command(pass_context=True)
    async def ping(self, ctx: commands.Context) -> None:
        """
                Responds with the latency time.
                Time took for Aryas to reply
                """
        before = time.monotonic()
        await self.bot.send_typing(ctx.message.author)
        after = time.monotonic()
        latency = int(round((after - before) * 1000))
        await self.bot.say('{}ms'.format(latency))

    @commands.command(pass_context=True)
    async def get_love(self, ctx: commands.Context, member: discord.Member) -> None:
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
            await send(self.bot, "{} doesn't have any ❤".format(member.mention, love), ctx.message.channel)
        else:
            await send(self.bot, '{} has {}x❤'.format(member.mention, love), ctx.message.channel)

    @commands.command(pass_context=True)
    async def show_love(self, ctx: commands.Context, member: discord.Member, love: int) -> None:
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

        c = conn.cursor()
        c.execute("""INSERT INTO love (giver, receiver, channel, server, amount) VALUES (?, ?, ?, ?, ?)""",
                  (giver.id,
                   member.id,
                   channel,
                   server,
                   love))
        conn.commit()
        await send(self.bot, '{} showed {}x❤ to {}'.format(giver.mention, love, member.mention), ctx.message.channel)

    @commands.command(pass_context=True)
    async def convert_currency(self, ctx: commands.Context, amount: float, base, to) -> None:
        """
        Calculates the requested currency conversion
        :param ctx: the message context
        :param amount: the amount to convert
        :param base: the base unit (e.g. USD, EUR)
        :param to: the conversion unit (e.g. ILS, GBP)
        """
        await self.bot.send_typing(ctx.message.channel)
        with request.urlopen('http://api.fixer.io/latest?base={}'.format(base)) as url:
            data = json.loads(url.read().decode())
            msg = '{} {} = {} {}'.format(amount, base, str(float(data['rates'][to]) * amount), to)
            await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def convert_length(self, ctx: commands.Context, amount: float, unit1, unit2) -> None:
        """
        Calculates the requested length conversion
        :param ctx: the message context
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the unit to convert to
        """
        try:
            value = (LEN_UNITS[unit1] / LEN_UNITS[unit2]) * amount
            await self.bot.say('{} {} = {} {}'.format(amount, unit1, value, unit2))
        except Exception as e:
            print(e)
            await send(self.bot, 'Could not covert {} {} to {}'.format(amount, unit1, unit2), ctx.message.channel, True)

    @commands.command(pass_context=True)
    async def convert_mass(self, ctx: commands.Context, amount: float, unit1, unit2) -> None:
        """
        Calculates the requested mass conversion
        :param ctx: the message context
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the unit to convert to
        """
        try:
            value = (MASS_UNITS[unit1] / MASS_UNITS[unit2]) * amount
            await self.bot.say('{} {} = {} {}'.format(amount, unit1, value, unit2))
        except Exception as e:
            print(e)
            await send(self.bot, 'Could not covert {} {} to {}'.format(amount, unit1, unit2), ctx.message.channel, True)

    @commands.command(pass_context=True)
    async def weather(self, ctx: commands.Context, country, city) -> None:
        """
        Gives info regarding the weather in a city
        :param ctx: the message context
        :param country: the country
        :param city: the city
        """

        owm = pyowm.OWM(CFG['weather']['api_key'])

        await self.bot.send_typing(ctx.message.channel)
        try:
            forecast = owm.weather_at_place('{},{}'.format(city, country))
            weather = forecast.get_weather()
            temperature = weather.get_temperature('celsius')['temp']
            await self.bot.say('The weather in {}, {} is {}° C'.format(country, city, temperature))
        except Exception as e:
            logger.error(e)
            await send(self.bot, 'Could not get the weather in {}, {}.'
                       .format(country, city), ctx.message.channel, True)

        # FIXME: Needs to update to use db instead of global status dictionary
        # @commands.command(pass_context=True)
        # @commands.has_role('Support')
        # async def setstatus(self, ctx, status):
        #     """
        #     Adds a status to the user.
        #     The status is used when the user is mentioned.
        #     :param ctx: The message context
        #     :param status: The status of the user (must be in possible_status)
        #     """
        #     name = ctx.message.author
        #
        #     if status in possible_status:
        #         if status != 'active':
        #             status[name] = status
        #         elif name in status:
        #             status.pop(name)
        #         await self.bot.say("You are now " + status)
        #
        #     else:
        #         await self.bot.say("You need to call it like choose a status in these : " + str(possible_status))
        #     await self.bot.delete_message(ctx.message)

        # async def on_mention(message, user_mentionned):
        #     """
        #                 When a mention happens, this function will be called, and handle it
        #                 :param message:     The message that contains the mention
        #                 :param user:        The mentionned user
        #                 """
        #     if user_mentionned in status:
        #         await self.bot.send_message(message.channel, "`" + user_mentionned.name + "` is " +
        #                                     status[user_mentionned])


def setup(bot: commands.Bot) -> None:
    bot.add_cog(General(bot))
