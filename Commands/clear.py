import asyncio
from discord.ext import commands

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
        if inumber <= 100:
            # Sends a deleted confirmation message
            await self.bot.purge_from(ctx.message.channel, limit=inumber + 1)
            msg = await self.bot.say(number + ' Message purged')
            # Waits 3.5 seconds and deleted the confirmation message.
            await asyncio.sleep(2)
            await self.bot.delete_message(msg)
        else:
            await self.bot.say('Cannot delete more than 100 messages at a time.')
