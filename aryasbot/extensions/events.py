import re

from discord.ext import commands

from ..utils import kick_user


class Events:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def on_message(self, message):
        """
        Checks for Discord server links in a message then
        kicks the member if links are found in their message
        """
        if message.author != self.bot.user:
            if 'Moderator' not in message.author.roles:
                pattern = 'discord.gg/[a-z0-9A-Z]+'
                # Uses the Discord server link pattern to look for links in a message using the re module
                if re.search(pattern, message.content):
                    reason = 'Advertising without permission'
                    await self.bot.delete_message(message)
                    await self.bot.send_message(message.author, 'Advertising is not allowed without permission!')
                    await kick_user(message.author, self.bot.user, message.server, self.bot, reason)


def setup(bot):
    bot.add_cog(Events(bot))
