from peewee import *
from src.db.aryasql import BaseModel


class User(BaseModel):
    id = PrimaryKeyField()
    discord_id = FixedCharField(18, unique=True, index=True)
    username = CharField()


class Message(BaseModel):
    id = PrimaryKeyField()
    discord_id = FixedCharField(18, index=True)
    user = ForeignKeyField(User, related_name='messages')
    body = CharField()


class Channel(BaseModel):
    id = PrimaryKeyField()
    discord_id = FixedCharField(18, index=True)


class Server(BaseModel):
    id = PrimaryKeyField()
    discord_id = FixedCharField(18, index=True)


class Love(BaseModel):
    id = PrimaryKeyField()
    amount = IntegerField()
    giver = ForeignKeyField(User, related_name='love_givers', index=True)
    receiver = ForeignKeyField(User, related_name='love_receivers', index=True)
    channel = ForeignKeyField(Channel)
