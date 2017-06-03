import discord
from discord.ext import commands

from Bot.Globals import MOD_LOG_CHANNEL_NAME
from Commands.utility import get_channel_by_name, send


def setup(bot):
    bot.add_cog(kick_module(bot))


class kick_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def kick(self, ctx, member: discord.Member, reason):
        """
        Kicks the mentioned user from the server
        :param ctx: the message context
        :param member: the member
        :param reason: the reason for the kick
        """
        try:
            await self.bot.kick(member)
            msg = '{} was kicked by {}. Reason: {}'.format(member.name, ctx.message.author.mention, reason)
            await send(self.bot, msg, get_channel_by_name(ctx.message.server, MOD_LOG_CHANNEL_NAME))
        except Exception as e:
            print(e)
            await send(self.bot, 'Failed to kick ' + member.mention, ctx.message.channel, True)
