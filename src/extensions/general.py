import discord
import pyowm
from discord.ext import commands
from discord.ext.commands import bot as bot_module
from src.utility import send, command_error, update_user_fields
from urllib import request
import json
import time
import datetime
from peewee import SQL, fn
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
        message.add_field(name='Rules', value=self.config.constants.rules, inline=False)
        message.set_footer(text='I am a bot BEEP BOOP')

        await self.bot.send_message(member, embed=message)

    @commands.command(pass_context=True, name='help')
    async def aryas_help(self, ctx, *commands):
        """Shows this message."""
        # Adapted from discord.ext.commands.bot._default_help_command.
        # The only thing that has been changed is the last send command
        # which now sends embeds instead of normal text messages
        bot = ctx.bot
        destination = ctx.message.author if bot.pm_help else ctx.message.channel

        def repl(obj):
            return bot_module._mentions_transforms.get(obj.group(0), '')

        # help by itself just lists our own commands.
        if len(commands) == 0:
            pages = bot.formatter.format_help_for(ctx, bot)
        elif len(commands) == 1:
            # try to see if it is a cog name
            name = bot_module._mention_pattern.sub(repl, commands[0])
            if name in bot.cogs:
                command = bot.cogs[name]
            else:
                command = bot.commands.get(name)
                if command is None:
                    await bot.send_message(destination, bot.command_not_found.format(name))
                    return

            pages = bot.formatter.format_help_for(ctx, command)
        else:
            name = bot_module._mention_pattern.sub(repl, commands[0])
            command = bot.commands.get(name)
            if command is None:
                await bot.send_message(destination, bot.command_not_found.format(name))
                return

            for key in commands[1:]:
                try:
                    key = bot_module._mention_pattern.sub(repl, key)
                    command = command.commands.get(key)
                    if command is None:
                        await bot.send_message(destination, bot.command_not_found.format(key))
                        return
                except AttributeError:
                    await bot.send_message(destination, bot.command_has_no_subcommands.format(command, key))
                    return

            pages = bot.formatter.format_help_for(ctx, command)
        for embed in pages:
            # This has been changed to send embeds
            await bot.send_message(destination, embed=embed)

    @commands.command(pass_context=True)
    async def whois(self, ctx: commands.Context, member: discord.Member) -> None:
        """
        Returns information about the given member
        :param ctx: the message context
        :param member: target member
        """
        user = self.orm.User.get_or_create(discord_id=member.id)[0]
        update_user_fields(user, member)

        if member.bot:
            message = discord.Embed(title=':robot: ' + member.name + '#' + member.discriminator,
                                    description=member.created_at.strftime('User since %b %d %Y'),
                                    timestamp=datetime.datetime.now(),
                                    color=self.config.embed_color)
        else:
            message = discord.Embed(title=member.display_name + '#' + member.discriminator,
                                    description=member.created_at.strftime('User since %b %d %Y'),
                                    timestamp=datetime.datetime.now(),
                                    color=self.config.embed_color)

        # send typing in case the db lookup takes a long time
        await self.bot.send_typing(ctx.message.channel)

        top_list = (self.orm.User
                    .select()
                    # peewee needs this to be ==
                    .where(self.orm.User.is_bot == False)
                    .order_by(self.orm.User.total_messages.desc())
                    .limit(1000))
        # if you're not in the top 1000 you're unranked
        rank = 'Unranked'
        for i, u in enumerate(top_list):
            if user == u:
                rank = '#{}'.format(i + 1)
                break

        # Finds the most posted on channel for the user
        # if the user hasn't posted anything it's None
        try:
            channel_id = (user.messages
                          .select(self.orm.Message.channel)
                          .join(self.orm.Server, on=(self.orm.Server.id == self.orm.Channel.server))
                          .switch(self.orm.Message)
                          # peewee needs this to be ==
                          .where(self.orm.Message.is_command == False, self.orm.Server.discord_id == member.server.id)
                          .annotate(self.orm.Channel)
                          .order_by(SQL('count').desc())
                          .limit(1))[0].channel.discord_id
        except IndexError:
            channel_id = None

        message.set_thumbnail(url=member.avatar_url)
        message.add_field(name='Status', value=str(member.status).capitalize())
        message.add_field(name='Favorite channel', value=self.bot.get_channel(channel_id))
        message.add_field(name='Total messages', value=user.total_messages)
        message.add_field(name='Rank', value=rank)
        message.add_field(name='ID', value=member.id)
        message.add_field(name='Joined', value=member.joined_at.strftime('%b %d %Y'))

        if member.game:
            message.add_field(name='Playing', value=member.game, inline=False)
        roles = [str(role) for role in member.roles]
        # @everyone is guaranteed to be the first rank, discard it
        roles.pop(0)
        if len(roles) > 0:
            message.add_field(name='Roles', value=', '.join(roles), inline=False)

        await self.bot.say(embed=message)

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
    async def get_love(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """
        Gives info regarding the amount of love a user has
        :param ctx: the message context
        :param member: the member
        """
        if member is None:
            member = ctx.message.author
        love = self.orm.User.get(discord_id=member.id).total_love

        if not love:
            send(self.bot, '{} doesn\'t have any ❤'.format(member.mention, love), ctx.message.channel)
        else:
            send(self.bot, '{} has {}x❤'.format(member.mention, love), ctx.message.channel)

    @commands.command(pass_context=True)
    async def show_love(self, ctx: commands.Context, member: discord.Member, love: int) -> None:
        """
        Gives love to a user
        :param ctx: the message context
        :param member: the member to give the love to
        :param love: the amount of love to give
        """

        if member == ctx.message.author:
            await command_error(ctx, 'You can\'t give yourself love!')

        if love < 0:
            await command_error(ctx, 'You can\'t give someone negative love!')
            return

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

        send(self.bot, '{} showed {}x❤ to {}'
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
        try:
            with request.urlopen('http://api.fixer.io/latest?base={}'.format(base)) as url:
                data = json.loads(url.read().decode())
                msg = '{} {} = {} {}'.format(amount, base, str(float(data['rates'][to]) * amount), to)
                await self.bot.say(msg)
        except Exception as e:
            self.config.logger.error(e)
            send(self.bot, 'Could not convert {} {} to {}'.format(amount, base, to), ctx.message.channel, True)

    @commands.command(pass_context=True)
    async def convert_length(self, ctx: commands.Context, amount: float, unit1, unit2) -> None:
        """
        Calculates the requested length conversion
        :param ctx: the message context
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the unit to convert to
        """
        len_units = self.config.constants.len_units
        try:
            value = (len_units[unit1] / len_units[unit2]) * amount
            await self.bot.say('{} {} = {} {}'.format(amount, unit1, value, unit2))
        except Exception as e:
            self.config.logger.error(e)
            send(self.bot, 'Could not convert {} {} to {}'.format(amount, unit1, unit2),
                 ctx.message.channel, True)

    @commands.command(pass_context=True)
    async def convert_mass(self, ctx: commands.Context, amount: float, unit1, unit2) -> None:
        """
        Calculates the requested mass conversion
        :param ctx: the message context
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the unit to convert to
        """
        mass_units = self.config.constants.mass_units
        try:
            value = (mass_units[unit1] / mass_units[unit2]) * amount
            await self.bot.say('{} {} = {} {}'.format(amount, unit1, value, unit2))
        except Exception as e:
            self.config.logger.error(e)
            send(self.bot, 'Could not convert {} {} to {}'.format(amount, unit1, unit2),
                 ctx.message.channel, True)

    @commands.command(pass_context=True)
    async def weather(self, ctx: commands.Context, city, country) -> None:
        """
        Gives info regarding the weather in a city
        :param ctx: the message context
        :param city: the city
        :param country: the country
        """

        owm = pyowm.OWM(self.config['weather']['api_key'])

        await self.bot.send_typing(ctx.message.channel)
        try:
            forecast = owm.weather_at_place('{},{}'.format(city, country))
            weather = forecast.get_weather()
            temperature = weather.get_temperature('celsius')['temp']
            await self.bot.say('The weather in {}, {} is {}° C'.format(city, country, temperature))
        except Exception as e:
            self.config.logger.error(e)
            send(self.bot, 'Could not get the weather in {}, {}.'
                 .format(country, city), ctx.message.channel, True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(General(bot))
