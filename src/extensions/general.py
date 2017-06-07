import discord
import pyowm
from discord.ext import commands
from src.utility import send
from urllib import request
import json
import time
# The following are imported purely for typehints, do not use directly.
from src.extensions.aryasorm import AryasORM
from src.extensions.config import Config


class General:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.orm: AryasORM = self.bot.cogs['AryasORM']
        self.config: Config = self.bot.cogs['Config']

    async def on_member_join(self, member: discord.Member):
        """
        Sends a private message to new users with welcome information
        :param member: the member
        """
        # Create embed
        title = 'Welcome to Developers'
        desc = 'Stuff that happens here'
        message = discord.Embed(title=title, description=desc, color=0xff80ff)
        message.add_field(name='Rules', value=self.config.rules, inline=False)
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
        love = self.orm.User.get(discord_id=member.id).total_love

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
        love = int(love)

        giver = self.orm.User.get_or_create(
            discord_id=msg.author.id
        )[0]
        receiver = self.orm.User.get_or_create(
            discord_id=member.id
        )[0]
        server = self.orm.Server.get_or_create(
            discord_id=msg.server.id
        )[0]
        channel = self.orm.Channel.get_or_create(
            discord_id=msg.channel.id,
            server=server.id
        )[0]

        self.orm.LoveTransaction.create(
            amount=love,
            giver=giver,
            receiver=receiver,
            channel=channel
        )

        await send(self.bot, '{} showed {}x❤ to {}'
                   .format(msg.author.mention, love, member.mention), ctx.message.channel)

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
        len_units = self.config.len_units
        try:
            value = (len_units / len_units) * amount
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
        mass_units = self.config.mass_units
        try:
            value = (mass_units[unit1] / mass_units[unit2]) * amount
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

        owm = pyowm.OWM(self.config['weather']['api_key'])

        await self.bot.send_typing(ctx.message.channel)
        try:
            forecast = owm.weather_at_place('{},{}'.format(city, country))
            weather = forecast.get_weather()
            temperature = weather.get_temperature('celsius')['temp']
            await self.bot.say('The weather in {}, {} is {}° C'.format(country, city, temperature))
        except Exception as e:
            self.config.logger.error(e)
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
