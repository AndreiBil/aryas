import sqlite3

conn = sqlite3.connect('aryas.db')

c = conn.cursor()

# Create table
c.execute("""CREATE TABLE love (giver char(18), receiver char(18), channel char(18), server char(18), amount integer)""")