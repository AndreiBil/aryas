"""
The database engine behind Aryas.
"""
from src.db.models import *
from peewee import MySQLDatabase
# from src.globals import logger

_database = MySQLDatabase(database='aryas', user='root', password='')


class AryaSQL:
    def __init__(self):
        # Connects to the database.
        self.db = _database

    @staticmethod
    def setup(force=False):
        """
        Setups the db by creating all relevant tables.
        :param force: Set to true if you want to drop the tables first
        """
        if force:
            User.drop_table()
            Message.drop_table()

        User.create_table()
        Message.create_table()

    @staticmethod
    def update():
        pass

class BaseModel(Model):
    class Meta:
        database = _database

