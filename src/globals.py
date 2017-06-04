import json
import logging
import sqlite3

conn: sqlite3.Connection = sqlite3.connect('aryas.db')

with open('secrets.json') as data_file:
    SECRETS = json.load(data_file)

# The possible status an User can have
possible_status = {'away', 'vacation', 'active'}

# Rules for the server
RULES = """1. Be polite.
2. Respect the opinion of others. ( Apple  > Android  tho and fuck anyone who says otherwise)
3. Don't spam.
4. Try Google before you ask questions here
5. Don't advertise any other discord server in any of the channels/DMs unless given permission by a mod/admin.
6. Use the appropriate channels for your question.
7. Don't have anything relevant to add in the programming channels? Stay quiet :smiley: :kissing_heart: 
8. Don't post any NSFW content.
9.  Use your common sense ¯\_(ツ)_/¯
10. Don't ask people for help in PMs. Use the designated channels instead.

11. But most importantly, HAVE FUN! That's so corny and cringy but I had to add that for the lulz

**Code formatting**
\```python
def your_awesome_func():
    return 1+1
\```
will produce
```python
def your_awesome_func():
    return 1+1
```"""

MESSAGE_SLEEP_TIME = 2
MOD_LOG_CHANNEL_NAME = 'mod_log'

# Setup logging.
logger = logging.getLogger('discord')
