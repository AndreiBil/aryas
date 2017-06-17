from discord.ext import commands
from discord.channel import PrivateChannel
from src.utility import is_command, update_user_fields
import datetime
from peewee import OperationalError
# Imported for type hints
from src.extensions.aryas_orm import AryasORM
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
        if not msg.channel.is_private:
            try:
                # append embeds list to message
                body = msg.content
                if msg.embeds:
                    body += '\n' + str(msg.embeds)

                user = self.orm.User.get_or_create(
                    discord_id=msg.author.id
                )[0]

                # Make sure to update the user so all relevant info is there
                update_user_fields(user, msg.author)

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
                    body=body,
                    is_command=is_command(self.bot, msg.content),
                    is_embed=True if msg.embeds else False
                )
            except OperationalError as e:
                self.config.logger.error(e)

    @commands.group(pass_context=True)
    @commands.has_any_role('Admin', 'Moderator', 'Support')
    async def stats(self, ctx: commands.Context):
        """
        Group of statistics commands
        :param ctx: the context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('`Usage: ?stats <subcommand>`')

    @stats.command(pass_context=True)
    async def online(self, ctx: commands.Context):
        """
        Show total online users on sever
        :param ctx: the context
        """
        server = ctx.message.server
        online = [1 if m.status != discord.Status.offline else 0 for m in server.members]
        await self.bot.say('{} users online'.format(sum(online)))

    @stats.group(pass_context=True)
    async def messages(self, ctx: commands.Context):
        """
        Group of message related commands
        :param ctx: the context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('`Usage: ?stats messages <subcommand>`')

    @messages.command(pass_context=True)
    async def total(self, ctx: commands.Context):
        """
        Show total amount of messages on server
        :param ctx: command context
        """
        server = self.orm.Server.get(discord_id=ctx.message.server.id)
        total_messages = await self.orm.query.server_total_messages(server)
        await self.bot.say('Total messages: {}'.format(total_messages))

    @messages.command(pass_context=True)
    async def users(self, ctx: commands.Context, count=10):
        """
        Show users with the most messages
        :param ctx: command context
        :param count: number of users, min 1, max 20
        """
        count = count
        # Show at least 1 user and 20 at most
        count = max(1, count)
        count = min(20, count)

        server = self.orm.Server.get(discord_id=ctx.message.server.id)
        users = await self.orm.query.user_top_list(count, server)

        embed = discord.Embed(color=discord.Color(self.config.constants.embed_color), timestamp=datetime.datetime.now())
        embed.set_footer(text='Global footer for all embeds', icon_url='https://cdn.discordapp.com/embed/avatars/2.png')

        for user in users:
            # the user might not have a name if s/he hasn't sent a message already
            # so in that case use the id instead
            name = user.name if user.name != '' else user.discord_id
            embed.add_field(name=name, value='Total messages: {}'.format(user.count), inline=False)

        await self.bot.say(content='Top active users:', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Statistics(bot))
