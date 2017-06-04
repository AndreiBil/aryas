import discord
from discord.ext import commands
import re
from src.utility import kick_user

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
        pattern = 'discord.gg/[a-z0-9A-Z]+'
         if re.search(pattern, message.content):
            reason = 'Advertising without permission'
            await self.bot.delete_message(message)
            await self.bot.send_message(message.author, 'Advertising is not allowed without permission!')
            await kick_user(message.author.name, self.bot.user.mention, message.server, self.bot, reason)
    
    await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(Events(bot))
