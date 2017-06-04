import MySQLdb
# from src.globals import logger


class Database:
    def __init__(self, db_name='aryas', mysql_user='root', mysql_password=''):
        try:
            self._db = MySQLdb.connect(db=db_name, user=mysql_user, password=mysql_password)
        except Exception as e:
            print(e)

    def create_table(self, table_name: str, columns: dict):
        """
        Creates MySQL table.

        :param table_name: 
        :type table_name: str
        :param columns: A dictionary of column name, type pairs
        :type columns: dict
        :return: 
        """
        c = self._db.cursor()
        try:
            c.execute("""CREATE TABLE test (
                         test1 INT)""")
        except Exception as e:
            # logger.error('Failed creating table: {}'.format(e))
            print('Failed creating table: {}'.format(e))


def main():
    db = Database()
    db.create_table('test', {})


if __name__ == '__main__':
    main()
