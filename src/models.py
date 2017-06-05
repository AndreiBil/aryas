from peewee import *
import datetime
from src.globals import DATABASE as _DATABASE


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
        database = _DATABASE


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
    # TODO: make this autoincrement
    total_messages = IntegerField(default=0)

    # def find_or_create(self, discord_id, server):
    #     """
    #     :param discord_id:
    #     :return: User model object.
    #     """
    #     # member = find(lambda m: m.name == 'Mighty', channel.server.members)
    #     try:
    #         user = discord.utils.find(lambda u: u.id == discord_id, server)
    #         self.create(
    #             discord_id=discord_id,
    #             username=user.username
    #         )
    #     except Exception as e:
    #         print(e)

    @property
    def total_love(self):
        total = 0
        for love in LoveTransaction.select().where(LoveTransaction.receiver == self):
            total += love.amount
        return total


class Message(DiscordModel):
    """
    Models a Discord message.
    """
    user = ForeignKeyField(User, related_name='messages')
    channel = ForeignKeyField(Channel, related_name='messages')
    server = ForeignKeyField(Server, related_name='messages')
    body = CharField()
    edited = DateTimeField(null=True)
    is_command = BooleanField(default=False)


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
