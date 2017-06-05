"""
The database engine behind Aryas.
"""
from discord.ext import commands

from src.globals import logger, DATABASE
from src.models import *


class AryasORM:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        # Connects to the database.
        self.db = DATABASE

        # Is there a nice way to scope all models within AryaORM? Still want them defined in a separate file.
        self.User = User
        self.Message = Message
        self.Channel = Channel
        self.Server = Server
        self.LoveTransaction = LoveTransaction

    async def setup(self, force=False):
        """
        Setups the db by creating all relevant tables.
        :param force: Set to true if you want to drop the tables first
        """
        if force:
            await self.drop_all_tables()
        else:
            try:
                self.db.create_tables([User, Message, Channel, Server, LoveTransaction])
            except OperationalError as e:
                logger.error(e)

    @staticmethod
    async def update_all():
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
            logger.error(e)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AryasORM(bot))
