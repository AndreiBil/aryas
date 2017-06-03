from discord.ext import commands

from Bot.Globals import possible_status, status


def setup(bot):
    bot.add_cog(setstatus_module(bot))


class setstatus_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Support')
    async def setstatus(self, ctx, stat):
        """
        Adds a status to the user.
        The status is used when the user is mentioned.
        :param ctx: The message context
        :param stat: The status of the user (must be in possible_status)
        """
        name = ctx.message.author

        if stat in possible_status:
            if stat != 'active':
                status[name] = stat
            else:
                status.pop(name)
            await self.bot.say("You are now " + stat)

        else:
            await self.bot.say("You need to call it like choose a status in these : " + str(possible_status))
        await self.bot.delete_message(ctx.message)
