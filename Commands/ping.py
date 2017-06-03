from discord.ext import commands


def setup(bot):
    bot.add_cog(ping_module(bot))


class ping_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self):
        await self.bot.say('Pong!')
