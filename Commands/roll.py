from random import randint

from discord.ext import commands


def setup(bot):
    bot.add_cog(roll_module(bot))


class roll_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def roll(self, ctx):
        """
        Rolls a dice and outputs a message depending on the result
        :param ctx: roll
        """
        randomdice = randint(1, 6)
        if randomdice < 4:
            await self.bot.say('{} rolled **{}**'.format(ctx.message.author.mention, randomdice))
        else:
            await self.bot.say(
                '{} The gods are with you, you rolled **{}**'.format(ctx.message.author.mention, randomdice))
