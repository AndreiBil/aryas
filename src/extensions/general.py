import discord


import pyowm


from discord.ext import commands





from src.globals import SECRETS, conn, logger


from src.utility import send


from src.globals import SECRETS, conn, logger


import asyncio


import time








class General:


    def __init__(self, bot):


        self.bot: commands.Bot = bot





    @commands.command(pass_context=True)


    async def ping(self, ctx):


        """


        Responds with the latency time.


        Time took for Aryas to reply


        """


        before = time.monotonic()


        await self.bot.send_typing(ctx.message.author)


        after = time.monotonic()


        latency = int(round((after - before) * 1000))


        await self.bot.say('{}ms'.format(latency))





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


    async def weather(self, ctx, country, city):


        """


        Gives info regarding the weather in a city


        :param ctx: the message context


        :param country: the country


        :param city: the city


        """


        owm = pyowm.OWM(SECRETS['weather']['api_key'])


        try:


            forecast = owm.weather_at_place('{},{}'.format(city, country))


            weather = forecast.get_weather()


            temperature = weather.get_temperature('celsius')['temp']


            await self.bot.say('The weather in {}, {} is {}° C'.format(country, city, temperature))


        except Exception as e:


            logger.error(e)


            await send(self.bot, 'Could not get the weather in {}, {}.'


                       .format(country, city), ctx.message.channel, True)





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





    # async def on_mention(message, user_mentionned):


    #     """


    #                 When a mention happens, this function will be called, and handle it


    #                 :param message:     The message that contains the mention


    #                 :param user:        The mentionned user


    #                 """


    #     if user_mentionned in status:


    #         await self.bot.send_message(message.channel, "`" + user_mentionned.name + "` is " + status[user_mentionned])


        


    #@commands.command(pass_context=True)


    #async def setreminder(self, ctx, string, hours, minutes):


    #    mins = int(minutes)


    #    hours = int(hours)


    #    mins += 60 * hours


    #    seconds = mins* 60





    #    if seconds > 86400:


    #        await self.bot.say('I can only remind you within 24 hours')


    #        return





    #    minutes = 'I will remind you about "{}" in '.format(string)





    #    if hours != 0:


    #        if hours == 1:


    #            message = '{} {} hour '.format(message, hours)


    #        else:


    #            message = '{} {} hours '.format(message, hours)





    #    if minutes != 0:


    #        if minutes == 1:


    #            message = '{} {} minute'.format(message, minutes)


    #        else:


    #            message = '{} {} minutes'.format(message, minutes)





    #    await self.bot.say(message)


    #    await asyncio.sleep(seconds)


    #    await self.bot.say('{} you told me to remind you about "{}"'.format(ctx.message.author.mention, string))








def setup(bot):


    bot.add_cog(General(bot))


