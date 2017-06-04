# Aryas-Bot
A bot for the Developers Discord server

## Deploying the bot with Docker
1. Setup a MySQL database called `aryas`

2. Run `setup.sh` like so:  
  
```
$ ./setup.sh YOUR_DISCORD_TOKEN YOUR_OWM_TOKEN
```

3. Run `run.sh` like so:  
  
```
$ ./run.sh
```

4. Add the bot to your server and run the `?setup` command to setup the database.
