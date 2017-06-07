"""
The database engine behind Aryas.
"""
from discord.ext import commands
from src.extensions.config import Config  # Imported for linting purposes only
from src.models import *


class AryasORM:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.config: Config = self.bot.cogs['Config']
        # Uses the database proxy object for our db as we don't know which database provider to use until runtime.
        self.db = database_proxy
        # Is there a nice way to scope all models within AryaORM? Still want them defined in a separate file.
        self.User = User
        self.Message = Message
        self.Channel = Channel
        self.Server = Server
        self.LoveTransaction = LoveTransaction

    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def setup(self, ctx, force=''):
        await self.bot.send_typing(ctx.message.channel)
        """
        Setups the db by creating all relevant tables.
        :param force: Set to true if you want to drop the tables first
        """
        try:
            if force == 'force':
                await self.drop_all_tables()
            else:
                self.db.create_tables([User, Message, Channel, Server, LoveTransaction])
        except Exception as e:
            self.config.logger.error(e)
            await self.bot.say('The setup did not complete:\n`{}`'.format(e))
            return

        await self.bot.say('Setup complete!')

    async def update_all(self):
        """
        Updates models to check for things like name changes, status changes etc.
        :return: 
        """
        pass

    async def drop_all_tables(self):
        """
        Drops all tables in the database.
        """
        try:
            self.db.drop_tables([User, Message, Channel, Server, LoveTransaction])
        except OperationalError as e:
            self.config.logger.error(e)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AryasORM(bot))
