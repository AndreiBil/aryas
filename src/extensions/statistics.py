from discord.ext import commands
from discord.channel import PrivateChannel
from src.utility import is_command
import datetime
from peewee import OperationalError
# Imported for type hints
from src.extensions.aryasorm import AryasORM
from src.extensions.config import Config
import discord


class Statistics:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.orm: AryasORM = self.bot.cogs['AryasORM']
        self.config: Config = self.bot.cogs['Config']

    async def on_message(self, msg: discord.Message):
        """
        Records the message and sender in the database. Also
        increments the users total messages.
        :param msg: the message
        """
        if not isinstance(msg.channel, PrivateChannel):
            try:
                user = self.orm.User.get_or_create(
                    discord_id=msg.author.id
                )[0]
                server = self.orm.Server.get_or_create(
                    discord_id=msg.channel.server.id
                )[0]
                channel = self.orm.Channel.get_or_create(
                    discord_id=msg.channel.id,
                    server=server
                )[0]
                self.orm.Message.create(
                    discord_id=msg.id,
                    user=user,
                    channel=channel,
                    body=msg.content,
                    is_command=is_command(self.bot, msg.content)
                )
                user.name = msg.author.name
                user.is_bot = msg.author.bot
                if not is_command(self.bot, msg.content):
                    user.total_messages += 1
                user.save()
            except OperationalError as e:
                self.config.logger.error(e)

    @commands.group(pass_context=True)
    @commands.has_role('Admin')
    async def stats(self, ctx: commands.Context):
        """
        Group of statistics commands
        :param ctx: the context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('`Usage: ?stats <subcommand>`')

    @stats.command(pass_context=True)
    @commands.has_role('Admin')
    async def online(self, ctx: commands.Context):
        """
        Show total online users on sever
        :param ctx: the context
        """
        server = ctx.message.server
        online = [1 if m.status != discord.Status.offline else 0 for m in server.members]
        await self.bot.say('{} users online'.format(sum(online)))

    @stats.group(pass_context=True)
    @commands.has_role('Admin')
    async def messages(self, ctx: commands.Context):
        """
        Group of message related commands
        :param ctx: the context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('`Usage: ?stats messages <subcommand>`')

    @messages.command()
    @commands.has_role('Admin')
    async def total(self):
        """
        Show total amount of messages on server
        """
        count = (self.orm.Message
                 .select(self.orm.Message, self.orm.User)
                 .join(self.orm.User)  # INNER join since every message has a user
                 # peewee needs this to be ==
                 .where(self.orm.Message.is_command == False, self.orm.User.is_bot == False)
                 .count())
        await self.bot.say('Total messages: {}'.format(count))

    @messages.command()
    @commands.has_role('Admin')
    async def users(self, count):
        """
        Show users with the most messages
        :param count: number of users, min 1, max 20
        """
        count = int(count)
        # Show at least 1 user and 20 at most
        count = max(1, count)
        count = min(20, count)

        users = (self.orm.User
                 .select()
                 # peewee needs this to be ==
                 .where(self.orm.User.is_bot == False)
                 .order_by(self.orm.User.total_messages.desc())
                 .limit(count))

        embed = discord.Embed(color=discord.Color(self.config.embed_color), timestamp=datetime.datetime.now())
        embed.set_footer(text='Global footer for all embeds', icon_url='https://cdn.discordapp.com/embed/avatars/2.png')
        for user in users:
            embed.add_field(name=user.name, value='Total messages: {}'.format(user.total_messages), inline=False)
        await self.bot.say(content='Top active users:', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Statistics(bot))
