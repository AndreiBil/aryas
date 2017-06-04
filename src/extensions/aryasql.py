"""
The database engine behind Aryas.
"""
from discord.ext import commands
from src.globals import logger, DATABASE
from src.models import *


class AryaSQL:
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        # Connects to the database.
        self.db = DATABASE

        # Is there a nice way to scope all models within AryaSQL? Still want them defined in a separate file.
        self.User = User
        self.Message = Message
        self.Channel = Channel
        self.Server = Server
        self.LoveTransaction = LoveTransaction

    def setup(self, force=False):
        """
        Setups the db by creating all relevant tables.
        :param force: Set to true if you want to drop the tables first
        """
        if force:
            try:
                self.User.drop_table()
                self.Message.drop_table()
                self.Channel.drop_table()
                self.Server.drop_table()
                self.LoveTransaction.drop_table()
            except OperationalError as e:
                logger.error(e)

        self.User.create_table()
        self.Message.create_table()
        self.Channel.create_table()
        self.Server.create_table()
        self.LoveTransaction.create_table()

    def update(self):
        pass


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AryaSQL(bot))

# The main method is only here for testing purposes
def main():
    aryas = AryaSQL()
    aryas.setup(force=True)


if __name__ == '__main__':
    main()
