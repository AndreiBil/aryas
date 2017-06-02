import sqlite3
import sys
from collections import defaultdict
import json


def main(argv):
<<<<<<< HEAD
    arg_dict = build_arg_list(argv)
=======
    arg_dict = build_arg_dict(argv)
>>>>>>> bb6974f8d362dd2b9a14a8ad10b729d03aeda8d7

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


<<<<<<< HEAD
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

=======
def build_arg_dict(argv):
    """
    Takes a list of system arguments and transforms them into a dictionary.
    :param argv: A tuple to 
    :return:  The argument dictionary
    """
    d = defaultdict(list)

    for index, arg in enumerate(argv):
        if index < len(argv) - 1:
            current_arg, next_arg = arg, argv[index+1]
        else:
            current_arg, next_arg = arg, None

        new_key = None

        # Double hyphen, equals
        if current_arg.startswith('--') and '=' in current_arg:
            new_key, val = current_arg.split('=')

        # Double hyphen, no equals
        # Single hyphen, no arg
        elif (current_arg.startswith('--') and '=' not in current_arg) or \
                (current_arg.startswith('-') and (not next_arg or next_arg.startswith('-'))):
            val = True

        # Single hyphen, arg
        elif current_arg.startswith('-') and next_arg and not next_arg.startswith('-'):
            val = next_arg

        else:
            if (next_arg is None) or (current_arg == val):
                continue

            else:
                raise ValueError('Unexpected argument pair: %s, %s' % (current_arg, next_arg))

        # Sanitize the key
        key = (new_key or current_arg).strip(' -')
        d[key].append(val)

    return dict(d)


>>>>>>> bb6974f8d362dd2b9a14a8ad10b729d03aeda8d7
if __name__ == '__main__':
    main(sys.argv[1:])