import discord
from discord.ext import commands
from src.utility import get_channel_by_name, send
from src.globals import MOD_LOG_CHANNEL_NAME


class ModTools:
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

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def ban(self, ctx, member: discord.Member, reason):
        """
        Bans the mentioned user from the server
        :param ctx: The message context
        :param member: The member to be banned
        :param reason: The reason for the ban
        """
        try:
            await self.bot.ban(member)
            msg = '{} was banned by {}. Reason: {}'.format(member.name, ctx.message.author.mention, reason)
            await send(self.bot, msg, get_channel_by_name(ctx.message.server, MOD_LOG_CHANNEL_NAME))
        except Exception as e:
            print(e)
            await send(self.bot, 'Failed to ban ' + member.mention, ctx.message.channel, True)

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def clear(self, ctx, number):
        """
        Purges messages from the channel
        :param ctx: The message context
        :param number: The number of messages to purge
        """
        inumber = int(number)
        if inumber <= 100:
            # In order to delete the command message too, the number of messages to clear is incremented
            await self.bot.purge_from(ctx.message.channel, limit=inumber + 1)
            await send(self.bot, number + ' Message cleared', ctx.message.channel, True)
        else:
            await send('Cannot delete more than 100 messages at a time.', ctx.message.channel, True)


def setup(bot):
    bot.add_cog(ModTools(bot))
