# Story_bot

Story bot is a bot for any channel, if you want to let user send you a storu to publish in channel with autoposting 

The bot is still under development  

----

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt

```bash
pip install -r requirements.txt
```

Create .env file following .env.example file instruction  

## Start bot on Linux  

To start using the bot you will need to run redis. Before you may need to install using the command  

```bash
sudo apt-get update
sudo apt-get install redis
```

Then restart redis and start the server with the following commands  

```bash
sudo service redis-server restart
redis-cli
```

Next, you need to start celery worker with the following command(console must be opened in working directory)

```bash
celery -A worker.celery worker -l info
```

In terminal use next command to start bot  

```bash
python3 main.py  
```

There is two type of cammnads in bot. For everyone:   

- /start  - Start using bot  

- /help  - See all comands  

- /mystory  -  Send story to admin

And for admin only:  

- /commercial  - Add a commercial to channel for everyday posting

- /news  -  Send to channel a news or some interesting fact

- /stories  -  If you didn't published any story, they will be send to you to send them in free time




