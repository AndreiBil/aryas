import discord # Imported for type hints
from discord.ext import commands
from src.utility import is_command
from src.globals import COLOR
from src.extensions.aryasorm import AryasORM  # Imported for type hints
import datetime


class Statistics:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.orm: AryasORM = self.bot.cogs['AryasORM']

    async def on_message(self, msg: discord.Message):
        """
        Records the message and sender in the database. Also
        increments the users total messages.
        :param msg: the message
        """
        if msg.author.bot or is_command(self.bot, msg.content):
            return
        user = self.orm.User.get_or_create(
            discord_id=msg.author.id
        )[0]
        self.orm.Message.create(
            discord_id=msg.id,
            user=user,
            body=msg.content
        )
        user.name = msg.author.name
        # TODO: autoincrement
        user.total_messages += 1
        user.save()

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def online(self, ctx: commands.Context):
        """
        Show total online users on sever
        :param ctx: the context
        """
        server = ctx.message.server
        online = [1 if m.status == discord.Status.online else 0 for m in server.members]
        await self.bot.say('{} users online'.format(sum(online)))

    @commands.group(pass_context=True)
    @commands.has_role('Admin')
    async def messages(self, ctx: commands.Context):
        """
        Group of message related commands
        :param ctx: the context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('`Usage: ?messages <subcommand>`')

    @messages.command()
    @commands.has_role('Admin')
    async def total(self):
        """
        Show total amount of messages on server
        """
        await self.bot.say('Total messages: {}'.format(self.orm.Message.select().count()))

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
        users = self.orm.User.select().order_by(self.orm.User.total_messages.desc()).limit(count)

        embed = discord.Embed(color=discord.Color(COLOR), timestamp=datetime.datetime.now())
        embed.set_footer(text='Global footer for all embeds', icon_url='https://cdn.discordapp.com/embed/avatars/2.png')
        for user in users:
            embed.add_field(name=user.name, value='Total messages: {}'.format(user.total_messages))
        await self.bot.say(content='Top active users:', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Statistics(bot))
