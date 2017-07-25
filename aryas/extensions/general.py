import discord
import pyowm
from discord.ext import commands
from discord.ext.commands import bot as bot_module
from ..utils.utility import send, command_error, update_user_fields, in_channel, in_bot_channel
from ..utils.converter import Converter
import time
import datetime
from googleapiclient.discovery import build
# The following are imported purely for typehints, do not use directly.
from . import AryasORM, Config


def setup(bot: commands.Bot) -> None:
    config: Config = bot.cogs['Config']
    orm: AryasORM = bot.cogs['AryasORM']
    check_channel = in_bot_channel(config)

    class General:
        async def on_member_join(self, member: discord.Member):
            """
            Sends a private message to new users with welcome information
            :param member: the member
            """
            # Create embed
            title = 'Welcome to Developers'
            message = discord.Embed(title=title, color=config.constants.embed_color, timestamp=datetime.datetime.now())
            message.add_field(name='General rules:', value=config.constants.rules_general, inline=False)
            message.add_field(name='Channel related rules:', value=config.constants.rules_channels, inline=False)
            message.add_field(name='Role related rules:', value=config.constants.rules_roles, inline=False)
            message.add_field(name='Code formatting:', value=config.constants.rules_code_formatting, inline=False)

            await bot.send_message(member, embed=message)

        @commands.command(pass_context=True, name='help')
        async def aryas_help(self, ctx, *commands_):
            """Shows this message."""
            # Adapted from discord.ext.commands.bot._default_help_command.
            # The only thing that has been changed is the last send command
            # which now sends embeds instead of normal text messages
            destination = ctx.message.author if bot.pm_help else ctx.message.channel

            def repl(obj):
                return bot_module._mentions_transforms.get(obj.group(0), '')

            # help by itself just lists our own commands.
            if len(commands_) == 0:
                pages = bot.formatter.format_help_for(ctx, bot)
            elif len(commands_) == 1:
                # try to see if it is a cog name
                name = bot_module._mention_pattern.sub(repl, commands_[0])
                if name in bot.cogs:
                    command = bot.cogs[name]
                else:
                    command = bot.commands.get(name)
                    if command is None:
                        await bot.send_message(destination, bot.command_not_found.format(name))
                        return

                pages = bot.formatter.format_help_for(ctx, command)
            else:
                name = bot_module._mention_pattern.sub(repl, commands_[0])
                command = bot.commands.get(name)
                if command is None:
                    await bot.send_message(destination, bot.command_not_found.format(name))
                    return

                for key in commands_[1:]:
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
        @check_channel
        async def whois(self, ctx: commands.Context, member: discord.Member) -> None:
            """
            Returns information about the given member
            """
            if not ctx.message.channel.is_private:
                user = orm.User.get_or_create(discord_id=member.id)[0]
                server = orm.Server.get(discord_id=member.server.id)
                update_user_fields(user, member)

                if member.bot:
                    message = discord.Embed(title=':robot: ' + member.display_name + '#' + member.discriminator,
                                            description=member.created_at.strftime('User since %b %d %Y'),
                                            timestamp=datetime.datetime.now(),
                                            color=config.constants.embed_color)
                else:
                    message = discord.Embed(title=member.display_name + '#' + member.discriminator,
                                            description=member.created_at.strftime('User since %b %d %Y'),
                                            timestamp=datetime.datetime.now(),
                                            color=config.constants.embed_color)

                # send typing in case the db lookup takes a long time
                await bot.send_typing(ctx.message.channel)

                users = await orm.query.user_top_list(1000, server)
                # if you're not in the top 1000 you're unranked
                rank = 'Unranked'
                for i, u in enumerate(users):
                    if user == u:
                        rank = '#{}'.format(i + 1)
                        break

                # Finds the most posted on channel for the user
                # if the user hasn't posted anything it's None
                try:
                    messages = await orm.query.channel_top_list(1, user, server)
                    channel_id = messages[0].channel.discord_id
                except IndexError:
                    channel_id = None

                total_messages = await orm.query.user_total_messages(user, server)

                message.set_thumbnail(url=member.avatar_url)
                message.add_field(name='Status', value=str(member.status).capitalize())
                message.add_field(name='Favorite channel', value=bot.get_channel(channel_id))
                message.add_field(name='Total messages', value=total_messages)
                message.add_field(name='Rank', value=rank)
                message.add_field(name='ID', value=member.id)
                message.add_field(name='Joined', value=member.joined_at.strftime('%b %d %Y'))

                if member.game:
                    message.add_field(name='Playing', value=member.game, inline=False)

                roles = [str(role) for role in member.roles]
                # @everyone is guaranteed to be the first role, discard it
                roles.pop(0)
                if len(roles) > 0:
                    message.add_field(name='Roles', value=', '.join(roles), inline=False)

                await bot.say(embed=message)
            else:
                config.logger.error('Cannot look up member in PrivateChannel')

        @commands.command(pass_context=True)
        @check_channel
        async def ping(self, ctx: commands.Context) -> None:
            """
            Responds with the latency time.
            Time took for Aryas to reply
            """
            before = time.monotonic()
            await bot.send_typing(ctx.message.author)
            after = time.monotonic()
            latency = int(round((after - before) * 1000))
            await bot.say('{}ms'.format(latency))

        @commands.command(pass_context=True)
        async def get_love(self, ctx: commands.Context, member: discord.Member = None) -> None:
            """
            Gives info regarding the amount of love a user has
            """
            if member is None:
                member = ctx.message.author
            love = orm.User.get(discord_id=member.id).total_love

            if not love:
                send(bot, '{} doesn\'t have any ❤'.format(member.mention, love), ctx.message.channel)
            else:
                send(bot, '{} has {}x❤'.format(member.mention, love), ctx.message.channel)

        @commands.command(pass_context=True)
        async def show_love(self, ctx: commands.Context, member: discord.Member, love: int) -> None:
            """
            Gives love to a user
            """

            if member == ctx.message.author:
                await command_error(ctx, 'You can\'t give yourself love!')

            if love < 0:
                await command_error(ctx, 'You can\'t give someone negative love!')
                return

            msg = ctx.message
            love = int(love)

            giver = orm.User.get_or_create(
                discord_id=msg.author.id
            )[0]
            receiver = orm.User.get_or_create(
                discord_id=member.id
            )[0]
            server = orm.Server.get_or_create(
                discord_id=msg.server.id
            )[0]
            channel = orm.Channel.get_or_create(
                discord_id=msg.channel.id,
                server=server.id
            )[0]

            orm.LoveTransaction.create(
                amount=love,
                giver=giver,
                receiver=receiver,
                channel=channel
            )

            send(bot, '{} showed {}x❤ to {}'
                 .format(msg.author.mention, love, member.mention), ctx.message.channel)

        @commands.command(pass_context=True)
        @check_channel
        async def convert(self, ctx: commands.Context, amount: float, unit1, unit2) -> None:
            """
            await bot.send_typing(ctx.message.channel)
            result = Converter.convert(amount, unit1, unit2)
            if result == -1:
                send(bot, 'Could not convert {} {} to {}'.format(amount, unit1, unit2), ctx.message.channel, True)
            else:
                await bot.say('{} {} = {} {}'.format(amount, unit1, result, unit2))
            Calculates the requested unit conversion
            """

        @commands.command(pass_context=True)
        @check_channel
        async def weather(self, ctx: commands.Context, city, country) -> None:
            """
            Gives info regarding the weather in a city
            """

            owm = pyowm.OWM(config['weather']['api_key'])

            await bot.send_typing(ctx.message.channel)
            try:
                forecast = owm.weather_at_place('{},{}'.format(city, country))
                weather = forecast.get_weather()
                temperature = weather.get_temperature('celsius')['temp']
                await bot.say('The weather in {}, {} is {}° C'.format(city, country, temperature))
            except Exception as e:
                config.logger.error(e)
                send(bot, 'Could not get the weather in {}, {}.'
                     .format(country, city), ctx.message.channel, True)

        @commands.command(pass_context=True)
        @commands.has_any_role('Support', 'Moderator', 'Admin')
        async def search(self, ctx: commands.Context) -> None:
            """
            Searches google, returns the title of the first 5 results along with their descriptions.
            Allows users to select a result then returns a link.
            """

            # Creates a service for the CSE, passes the
            # search terms to the service, and sets safesearch to medium
            # result is a dictionary with list values
            service = build(config['google']['cse_name'], "v1", developerKey=config['google']['api_key'])
            query = str(ctx.message.content.lstrip("$search"))
            result = service.cse().list(q=query, cx=config['google']['cse_id'], safe="medium",).execute()

            try:
                if 'items' in result and len(result['items']) > 0:
                    lst = "**Search results:** \n"
                    if len(result['items']) >= 5:
                        items = 5
                    else:
                        items = len(result['items'])
                    for i in range(items):
                        lst += "**{}. {}**\n{}\n"\
                               .format(i+1, result['items'][i]['title'], result['items'][i]['snippet'])
                    send(bot, lst, ctx.message.channel, delete=True, time=20, show_dots=True)
                    response = await bot.wait_for_message(
                        timeout=20, author=ctx.message.author,
                        channel=ctx.message.channel,
                        check=lambda m: m.content.isnumeric() and int(m.content) in range(1, 6))
                    if response:
                        await bot.send_typing(ctx.message.channel)
                        link = result['items'][int(response.content)-1]['link']
                        await bot.send_message(ctx.message.channel, link)
                else:
                    await bot.send_message(ctx.message.channel, 'No results found.')
            except Exception as e:
                config.logger.error(e)
                await bot.send_message(ctx.message.channel, "Something went wrong while googling.")

    bot.add_cog(General())
