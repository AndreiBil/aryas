"""
The database engine behind Aryas.
"""
from discord.ext import commands
from peewee import OperationalError

from src.extensions.config import Config  # Imported for linting purposes only
from src.models import get_models


class AryasORM:
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.config: Config = self.bot.cogs['Config']
        # Uses the database proxy object for our db as we don't know which database provider to use until runtime.
        self.db, self.models = get_models(self.config)

        # Is there a nice way to scope all models within AryaORM? Still want them defined in a separate file.
        # Have I got a surprise for you, my dear Tom
        self.User = self.models.User
        self.Message = self.models.Message
        self.Channel = self.models.Channel
        self.Server = self.models.Server
        self.LoveTransaction = self.models.LoveTransaction

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
                self.db.create_tables([self.models.User, self.models.Message, self.models.Channel, self.models.Server,
                                       self.models.LoveTransaction])
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
            self.db.drop_tables([self.models.User, self.models.Message, self.models.Channel, self.models.Server,
                                 self.models.LoveTransaction])
        except OperationalError as e:
            self.config.logger.error(e)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AryasORM(bot))
