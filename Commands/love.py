import discord
from discord.ext import commands

from Bot.Globals import conn
from Commands.utility import send


def setup(bot):
    bot.add_cog(Love_module(bot))


class Love_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def get_love(self, ctx, member: discord.Member):
        """
        Gives info regarding the amount of love a user has
        :param ctx: the message context
        :param member: the member
        """
        c = conn.cursor()
        # The comma next to user_id needs to be there, don't ask me why.
        c.execute("""SELECT SUM(amount) FROM love WHERE receiver=? """, (member.id,))
        love = c.fetchone()[0]

        if not love:
            await send(self.bot, "{} doesn't have any ❤".format(member.mention, love), ctx.message.channel)
        else:
            await send(self.bot, '{} has {}x❤'.format(member.mention, love), ctx.message.channel)

    @commands.command(pass_context=True)
    async def show_love(self, ctx, member: discord.Member, love):
        """
        Gives love to a user
        :param ctx: the message context
        :param member: the member to give the love to
        :param love: the amount of love to give
        """
        msg = ctx.message
        giver = ctx.message.author
        channel = msg.channel.id
        server = msg.server.id
        love = int(love)

        c = conn.cursor()
        c.execute("""INSERT INTO love (giver, receiver, channel, server, amount) VALUES (?, ?, ?, ?, ?)""",
                  (giver.id,
                   member.id,
                   channel,
                   server,
                   love))
        conn.commit()
        await send(self.bot, '{} showed {}x❤ to {}'.format(giver.mention, love, member.mention), ctx.message.channel)
