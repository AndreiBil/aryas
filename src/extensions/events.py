import re
from discord.ext import commands
from src.utility import kick_user
from src.globals import raid_mode

class Events:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def on_message(self, message):
        """
        Checks for Discord server links in a message then
        kicks the member if links are found in their message
        """
        if message.author != self.bot.user:
            if 'Admin' not in message.author.roles:
				#Checks if the server is in Anti-Raid mode
				if not raid_mode:
					pattern = 'discord.gg/[a-z0-9A-Z]+'
					# Uses the Discord server link pattern to look for links in a message using the re module
					if re.search(pattern, message.content):
						reason = 'Advertising without permission'
						await self.bot.delete_message(message)
						await self.bot.send_message(message.author, 'Advertising is not allowed without permission!')
						await kick_user(message.author, self.bot.user, message.server, self.bot, reason)
				else:
					await self.bot.delete_message(message)

def setup(bot):
    bot.add_cog(Events(bot))