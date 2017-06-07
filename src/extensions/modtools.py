import discord
from discord.ext import commands
from src.utility import get_channel_by_name, send
from src.globals import MOD_LOG_CHANNEL_NAME, raid_mode


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
    async def clear(self, ctx: commands.Context, number: int) -> None:
        """
        Purges messages from the channel
        :param ctx: The message context
        :param number: The number of messages to purge
        """
        if number <= 100:
            # In order to delete the command message too, the number of messages to clear is incremented
            msgs = await self.bot.purge_from(ctx.message.channel, limit=number + 1)
            # msgs also contains the clear command message itself, so the actual number of cleared messages is the
            # number of messages cleared minus one
            await send(self.bot, '{} message(s) cleared.'.format(len(msgs) - 1), ctx.message.channel, True)
        else:
            await send(self.bot, 'Cannot delete more than 100 messages at a time.', ctx.message.channel, True)

	@commands.command(pass_context=True)
    @commands.has_role('Admin')
	async def panic(ctx):
		"""
		Sets a bool for Anti-Raid mode
		"""
		if raid_mode:
			raid_mode = False
			await send(self.bot, 'Anti-Raid mode disabled!', ctx.message.channel, False)
		else:
			raid_mode = True
			await send(self.bot, 'Anti-Raid mode enabled!', ctx.message.channel, False)


def setup(bot):
    bot.add_cog(ModTools(bot))