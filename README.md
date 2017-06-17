# Aryas-Bot
A bot for the Developers Discord server

## Running the bot

#### With Docker:
1. Clone the repo and `cd` into its root folder.
2. `$ docker build . -t aryas_bot`
3. `$ ./run.sh`
4. `$ docker rm -f [CONTAINER HASH]`
5. Edit `~/.aryas/cfg.json`, add the necessary API keys.
6. `$ ./run.sh`

#### Without Docker:
1. Clone the repo and `cd` into its root folder.
2. `$ pip3 install -r requirements.txt`
3. `$ python3 setup.py install`
4. `$ aryas` *(This will will fail, you should get an error about `cfg.json` being missing)*
5. Edit `~/.aryas/cfg.json`, add the necessary API keys.
6. `$ aryas`