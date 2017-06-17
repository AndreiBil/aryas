"""
The database engine behind Aryas.
"""
from discord.ext import commands
from peewee import OperationalError, SQL

from .config import Config  # Imported for linting purposes only
from ..utils import models


class Query:
    """
    This class acts as a namespace for useful queries
    """

    def __init__(self, models_):
        self.models = models_

    async def channel_top_list(self, count, user, server):
        """
        Gets top <count> channels for a user
        :param count: length of top list
        :param user: the user
        :param server: the server
        :return: a SelectQuery with Message.channel with the top channels
        """
        messages = (user.messages
                    .select(self.models.Message.channel)
                    .join(self.models.Server, on=(self.models.Server.id == self.models.Channel.server))
                    .switch(self.models.Message)
                    # peewee needs the ==
                    .where(self.models.Message.is_command == False,
                           self.models.Server.id == server)
                    .annotate(self.models.Channel)
                    .order_by(SQL('count').desc())
                    .limit(count))
        return messages

    async def user_top_list(self, count, server):
        """
        Gets top <count> users on the server
        :param count: length of the top list
        :param server: the server
        :return: a SelectQuery with users on the top list
        """
        users = (self.models.User
                 .select()
                 .join(self.models.Channel, on=(self.models.Channel.id == self.models.Message.channel))
                 .join(self.models.Server, on=(self.models.Server.id == self.models.Channel.server))
                 .switch(self.models.User)
                 # peewee needs the ==
                 .where(self.models.Message.is_command == False,
                        self.models.User.is_bot == False,
                        self.models.Server.id == server)
                 .annotate(self.models.Message)  # annotate alias to 'count'
                 .order_by(SQL('count'))
                 .limit(count))
        return users

    async def user_total_messages(self, user, server):
        """
        Gets the total amount of messages by the user on the server
        :param user: the user
        :param server: the server
        :return: total count of messages by the user
        """
        total_messages = (user.messages
                          .join(self.models.Channel, on=(self.models.Channel.id == self.models.Message.channel))
                          .join(self.models.Server, on=(self.models.Server.id == self.models.Channel.server))
                          # peewee needs the ==
                          .where(self.models.Message.is_command == False,
                                 self.models.Server.id == server)
                          .count())
        return total_messages

    async def server_total_messages(self, server):
        """
        Gets the total amount of messages on the server
        :param server: the server
        :return: total count of messages on server
        """
        total_messages = (self.models.Message
                          .select()
                          .join(self.models.User, on=(self.models.User.id == self.models.Message.user))
                          .join(self.models.Channel, on=(self.models.Channel.id == self.models.Message.channel))
                          .join(self.models.Server, on=(self.models.Server.id == self.models.Channel.server))
                          # peewee needs the ==
                          .where(self.models.Message.is_command == False,
                                 self.models.User.is_bot == False,
                                 self.models.Server.id == server)
                          .count())
        return total_messages


class AryasORM:
    def __init__(self, bot):
        self.bot = bot  # type: commands.Bot
        self.config = self.bot.cogs['Config']  # type: Config
        # Uses the database proxy object for our db as we don't know which database provider to use until runtime.
        self.db, self.models = models.get_models(self.config)
        self.query = Query(self.models)

        # Is there a nice way to scope all models within AryaORM? Still want them defined in a separate file.
        # Have I got a surprise for you, my dear Tom
        self.User = self.models.User
        self.Message = self.models.Message
        self.Channel = self.models.Channel
        self.Server = self.models.Server
        self.LoveTransaction = self.models.LoveTransaction

        self.make_tables()

    def make_tables(self):
        """
        Setups the db by creating all relevant tables IF they don't aready exist.
        """
        try:
            self.db.create_tables([self.models.User, self.models.Message, self.models.Channel, self.models.Server,
                                   self.models.LoveTransaction], safe=True)
        except Exception as e:
            self.config.logger.error(e)
            return

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
                                 self.models.LoveTransaction], safe=True)
        except OperationalError as e:
            self.config.logger.error(e)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AryasORM(bot))
