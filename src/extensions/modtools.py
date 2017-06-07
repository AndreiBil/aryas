import discord
from discord.ext import commands
from src.utility import get_channel_by_name, send, command_error
from src.globals import MOD_LOG_CHANNEL_NAME


class ModTools:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def kick(self, ctx: commands.Context, member: discord.Member, *reason) -> None:
        """
        Kicks the mentioned user from the server
        :param ctx: the message context
        :param member: the member
        :param reason: the reason for the kick
        """
        try:
            await self.bot.kick(member)
            msg = '{} was kicked by {}. Reason: {}'.format(member.name, ctx.message.author.mention, ' '.join(reason))
            await send(self.bot, msg, get_channel_by_name(ctx.message.server, MOD_LOG_CHANNEL_NAME))
        except Exception as e:
            print(e)
            await send(self.bot, 'Failed to kick ' + member.mention, ctx.message.channel, True)

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def ban(self, ctx: commands.Context, member: discord.Member, *reason) -> None:
        """
        Bans the mentioned user from the server
        :param ctx: The message context
        :param member: The member to be banned
        :param reason: The reason for the ban
        """
        try:
            await self.bot.ban(member)
            msg = '{} was banned by {}. Reason: {}'.format(member.name, ctx.message.author.mention, ' '.join(reason))
            await send(self.bot, msg, get_channel_by_name(ctx.message.server, MOD_LOG_CHANNEL_NAME))
        except Exception as e:
            print(e)
            await send(self.bot, 'Failed to ban ' + member.mention, ctx.message.channel, True)

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def clear(self, ctx: commands.Context, number: int, member: discord.Member=None) -> None:
        """
        Purges messages from the channel
        :param ctx: The message context
        :param number: The number of messages to purge
        :param member: The member whose messages will be cleared
        """

        if number < 1:
            await command_error(ctx, "You must attempt to purge at least 1 message!")
            return

        def predicate(msg: discord.Message) -> bool:
            return msg == ctx.message or member is None or msg.author == member

        if number <= 100:
            #  Add 1 to limit to include command message, subtract 1 from the return to not count it.
            msgs = await self.bot.purge_from(ctx.message.channel, limit=number+1, check=predicate)
            await send(self.bot, '{} message{} cleared.'.format(len(msgs)-1, "s" if len(msgs)-1 != 1 else ""),
                       ctx.message.channel, True)
        else:
            await command_error(ctx, 'Cannot delete more than 100 messages at a time.')


def setup(bot):
    bot.add_cog(ModTools(bot))
