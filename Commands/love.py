from discord.ext import commands

from Bot.Globals import conn


def setup(bot):
    bot.add_cog(Love_module(bot))


class Love_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def get_love(self, ctx, mention):
        user_id = ctx.message.raw_mentions[0]

        c = conn.cursor()
        # The comma next to user_id needs to be there, don't ask me why.
        c.execute("""SELECT SUM(amount) FROM love WHERE receiver=? """, (user_id,))
        love = c.fetchone()[0]

        if not love:
            await self.bot.say("<@{}> doesn't have any ❤".format(user_id, love))
        else:
            await self.bot.say('<@{}> has {}x❤'.format(user_id, love))

    @commands.command(pass_context=True)
    async def show_love(self, ctx, mention, love):
        msg = ctx.message

        giver = ctx.message.author
        receiver = msg.raw_mentions[0]
        channel = msg.channel.id
        server = msg.server.id
        love = int(love)

        c = conn.cursor()
        c.execute("""INSERT INTO love (giver, receiver, channel, server, amount) VALUES (?, ?, ?, ?, ?)""",
                  (giver.id,
                   receiver,
                   channel,
                   server,
                   love))
        conn.commit()
        await self.bot.say('<@{}> showed {}x❤ to {}'.format(giver.id, love, mention))
