from peewee import *
import datetime
from src.extensions.config import Config

_config = Config()
database_proxy = _config.db['database_proxy']

# Based on the `env` config variable, use a different database provider
if _config.env == 'dev':
    database = SqliteDatabase(_config.cache_dir + _config.db['name'] + '.db')
elif _config.env == 'prod':
    database = MySQLDatabase(
        database=_config.db['name'],
        user=_config.db['user'],
        password=_config.db['pass'],
        host=_config.db['host'],
        charset='utf8mb4'
    )
else:
    raise Exception('{} is not a valid environment.'.format(_config.env))


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
        # Uses the global database currently. Will use env vars to potentially differentiate between different
        # environments in the future eg. production env uses MySQL, dev env uses SQLite
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

database_proxy.initialize(database)
