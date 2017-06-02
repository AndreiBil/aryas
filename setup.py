import sqlite3
import sys
from collections import defaultdict
import json


def main(argv):
    arg_dict = build_arg_list(argv)

    if 'discord_token' in arg_dict:
        # Create a SQLite DB and connect to it.
        conn = sqlite3.connect('aryas.db')
        c = conn.cursor()
        # Create love table
        c.execute("""CREATE TABLE IF NOT EXISTS love 
                      (giver CHAR(18), receiver CHAR(18), channel CHAR(18), server CHAR(18), amount INTEGER)""")

        # Create secrets.json file. Declared object inline for brevity.
        json_data = json.dumps({
            'discord': {
                'token': arg_dict['discord_token'][0]
            }
        }, sort_keys=True, indent=2, separators=(',', ': '))

        # Write json_data to the secrets.json file.
        with open('secrets.json', 'w') as outfile:
            outfile.write(json_data)
    else:
        return print('Please supply a discord_token')


def build_arg_list(argv):
    """
    Takes a list of system arguments and transforms them into a dictionary.
    :param argv: ie. sys.argv[1:]
    :return d:  The argument dictionary
    """
    d = defaultdict(list)
    for k, v in ((k.lstrip('-'), v) for k, v in (a.split('=') for a in argv)):
        d[k].append(v)

    return dict(d)

if __name__ == '__main__':
    main(sys.argv[1:])