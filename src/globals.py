import json
import logging
import sqlite3

CACHE_DIR = "./.aryas/"

conn: sqlite3.Connection = sqlite3.connect(CACHE_DIR+'aryas.db')


with open(CACHE_DIR+'cfg.json') as data_file:
    CFG = json.load(data_file)

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

MESSAGE_SLEEP_TIME = 3
MOD_LOG_CHANNEL_NAME = 'mod_log'
LEN_UNITS = {'millimeter': 0.001, 'centimeter': 0.01, 'meter': 1, 'kilometer': 1000,
             'inch': 0.0254, 'foot': 3.28084, 'yard': 1.09361}
MASS_UNITS = {'milligram': 0.000001, 'gram': 0.001, 'kilogram': 1, 'ton': 1000,
              'pound': 0.453592, 'ounce': 0.0283495}

# Setup logging.
logger = logging.getLogger('discord')
