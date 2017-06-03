import discord
from random import randint
from discord.ext import commands
from src.utility import send
from src.globals import conn


class General:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self):
        await self.bot.say('Pong')

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

        # FIXME: Needs to update to use db instead of global status dictionary
        # @commands.command(pass_context=True)
        # @commands.has_role('Support')
        # async def setstatus(self, ctx, status):
        #     """
        #     Adds a status to the user.
        #     The status is used when the user is mentioned.
        #     :param ctx: The message context
        #     :param status: The status of the user (must be in possible_status)
        #     """
        #     name = ctx.message.author
        #
        #     if status in possible_status:
        #         if status != 'active':
        #             status[name] = status
        #         elif name in status:
        #             status.pop(name)
        #         await self.bot.say("You are now " + status)
        #
        #     else:
        #         await self.bot.say("You need to call it like choose a status in these : " + str(possible_status))
        #     await self.bot.delete_message(ctx.message)

        # @commands.command(pass_context=True)
        # @commands.has_role('Support')
        # async def setstatus(self, ctx, status):
        #     """
        #     Adds a status to the user.
        #     The status is used when the user is mentioned.
        #     :param ctx: The message context
        #     :param stat: The status of the user (must be in possible_status)
        #     """
        #     name = ctx.message.author
        #     if stat in possible_status:
        #         if stat != 'active':
        #             status[name] = stat
        #         elif name in status:
        #             status.pop(name)
        #         await self.bot.say("You are now " + stat)
        #
        #     else:
        #         await self.bot.say("You need to call it like choose a status in these : " + str(possible_status))
        #     await self.bot.delete_message(ctx.message)
        # async def on_mention(message, user_mentionned):
        #     """
        #                 When a mention happens, this function will be called, and handle it
        #                 :param message:     The message that contains the mention
        #                 :param user:        The mentionned user
        #                 """
        #     if user_mentionned in status:
        #         await self.bot.send_message(message.channel, "`" + user_mentionned.name + "` is " + status[user_mentionned])


def setup(bot):
    bot.add_cog(General(bot))