import datetime

from peewee import *

from src.extensions.config import Config as _Config


class Models:
    def __init__(self, user, server, channel, message, server_nick, love_transaction):
        self.User = user
        self.Server = server
        self.Channel = channel
        self.Message = message
        self.ServerNick = server_nick
        self.LoveTransaction = love_transaction


def get_models(config: _Config) -> (Proxy, Models):

    db_cfg = config.db
    database_proxy = db_cfg["_db_proxy"]

    # Based on the `env` config variable, use a different database provider
    if config.constants.env == 'dev':
        database_ = SqliteDatabase(config.constants.cache_dir + 'aryas.db')
    elif config.constants.env == 'prod':
        database_ = MySQLDatabase(
            database=db_cfg['name'],
            user=db_cfg['user'],
            password=db_cfg['pass'],
            host=db_cfg['host'],
            charset='utf8mb4'
        )
    else:
        raise Exception('{} is not a valid environment.'.format(config.constants.env))

    class BaseModel(Model):
        """
        The base model
        """
        # All models have an auto incrementing integer primary key.
        id = PrimaryKeyField()
        created_at = DateTimeField(default=datetime.datetime.now)
        updated_at = DateTimeField()

        def save(self, *args, **kwargs):
            self.updated_at = datetime.datetime.now()
            return super(BaseModel, self).save(*args, **kwargs)

        class Meta:
            database = database_proxy

    class DiscordModel(BaseModel):
        """
        Applies to everything that directly models a discord object eg. User, Server, Channel, Message
        """
        discord_id = FixedCharField(18, index=True, unique=True)

    class User(DiscordModel):
        """
        Models a Discord user.
        Whereas the discord.py library has sub classes such as Member, this is not relevant in db-land.
        """
        name = CharField(default='')
        game = CharField(default='')
        status = CharField(default='')
        discriminator = CharField(default='')
        top_role = CharField(default='')
        is_bot = BooleanField(default=False)
        notes = TextField(default='')
        # TODO: make this autoincrement
        total_messages = IntegerField(default=0)

        @property
        def total_love(self):
            total = 0
            for love in LoveTransaction.select().where(LoveTransaction.receiver == self):
                total += love.amount
            return total

    class Server(DiscordModel):
        """
        Models a Discord Server.
        """
        pass

    class Channel(DiscordModel):
        """
        Models a Discord channel.
        """
        server = ForeignKeyField(Server, related_name='channels')

class Message(DiscordModel):
    """
    Models a Discord message.
    """
    user = ForeignKeyField(User, related_name='messages')
    channel = ForeignKeyField(Channel, related_name='messages')
    body = TextField()
    edited = DateTimeField(null=True)
    is_command = BooleanField(default=False)
    is_embed = BooleanField(default=False)

    class ServerNick(BaseModel):
        """
        Stores the relationship between servers and users' nicknames.
        """
        user = ForeignKeyField(User)
        server = ForeignKeyField(Server)

        class Meta:
            primary_key = CompositeKey('user', 'server')

    class LoveTransaction(BaseModel):
        """
        Models a love transaction. When one user shows love to another, this is a transaction.
        """
        amount = IntegerField()
        giver = ForeignKeyField(User, related_name='love_givers', index=True)
        receiver = ForeignKeyField(User, related_name='love_receivers', index=True)
        channel = ForeignKeyField(Channel)

    models = Models(User, Server, Channel, Message, ServerNick, LoveTransaction)

    database_proxy.initialize(database_)
    return database_proxy, models
