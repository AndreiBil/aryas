from discord.ext import commands

from Bot.Globals import MAX_CLEAR_NUM
from Commands.utility import send


def setup(bot):
    bot.add_cog(clear_module(bot))


class clear_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def clear(self, ctx, number):
        """
        Purges messages from the channel
        :param ctx: The message context
        :param number: The number of messages to purge
        """
        inumber = int(number)
        if inumber <= MAX_CLEAR_NUM:
            # In order to delete the command message too, the number of messages to clear is incremented
            await self.bot.purge_from(ctx.message.channel, limit=inumber + 1)
            await send(self.bot, number + ' Message cleared', ctx.message.channel, True)
        else:
            await send('Cannot delete more than 100 messages at a time.', ctx.message.channel, True)
