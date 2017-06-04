import discord
from discord.ext import commands
import re

class Events:
  def __init__(self, bot):
    self.bot: commands.Bot = Bot
  
  @commands.event
  async def on_message(self, message):
    """
    Checks for Discord server links in a message
    then kicks members if links are found
    """
    if message.author != self.bot.user:
      if 'Moderator' not in message.author.roles:
        pattern1 = 'https://discord.gg/[a-z0-9A-Z]+'
        pattern2 = 'discord.gg/[a-z0-9A-Z]+'
         if re.search(pattern1, message.content) or re.search(pattern2, message.content):
            await self.bot.delete_message(message)
            await self.bot.send_message(message.author, 'Advertising is not allowed without permission!')
            await self.bot.kick(message.author)

def setup(bot):
    bot.add_cog(Events(bot))
