import discord
import pyowm
from discord.ext import commands
from src.extensions.aryasorm import AryasORM  # Imported purely for typehints, do not use directly.
from src.globals import SECRETS, logger
from src.utility import send
import time


class General:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.orm: AryasORM = self.bot.cogs['AryasORM']

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
    async def show_love(self, ctx: commands.Context, member: discord.Member, love: str) -> None:
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
    async def weather(self, ctx: commands.Context, country, city) -> None:
        """
        Gives info regarding the weather in a city
        :param ctx: the message context
        :param country: the country
        :param city: the city
        """
        owm = pyowm.OWM(SECRETS['weather']['api_key'])
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
