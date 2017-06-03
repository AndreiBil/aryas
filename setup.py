import json
import sqlite3
import sys
from collections import defaultdict

EXPECTED_ARGS = ['discord_token', 'OpenWeatherMap_api_key']


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


def create_secret_json(**kwargs):
    """
    Create secrets.json file.
    :param kwargs: dictionary of json object properties
    """
    # FIXME: make the creation of the secrets.json file modular, so if you change the required arguments you
    # would only need to change the collection of expected arguments
    json_data = json.dumps({
        'discord': {
            'token': kwargs['discord_token'][0]
        },
        'weather': {
            'api_key': kwargs['OpenWeatherMap_api_key'][0]
        }
    }, sort_keys=True, indent=2, separators=(',', ': '))

    # Write json_data to the secrets.json file.
    with open('secrets.json', 'w') as outfile:
        outfile.write(json_data)


def create_love_table():
    """
    Creates a love table on a SQLite DB
    """
    # Create a SQLite DB and connect to it.
    conn = sqlite3.connect('aryas.db')
    c = conn.cursor()
    # Create love table
    c.execute("""CREATE TABLE IF NOT EXISTS love
                  (giver CHAR(18), receiver CHAR(18), channel CHAR(18), server CHAR(18), amount INTEGER)""")


def main(argv):
    """
    Creates a love table, and the secret json file
    :param argv: the arguments
    """
    arg_dict = build_arg_list(argv)

    for arg in EXPECTED_ARGS:
        if arg not in arg_dict:
            arg_dict[arg] = input('Enter {}: '.format(arg))

    create_love_table()
    create_secret_json(**arg_dict)

if __name__ == '__main__':
    main(sys.argv[1:])
