# Fusion Club Ad Master - Telegram Bot #
## General information ##
Please, join to Telegram Messanger group [Чат бот для Fusion Club](https://t.me/joinchat/A1CpsBikC2CA31ExnyYAGg) if you would like to help or discuss this project.
***

#### This bot won't work out of the box, it requires to install MongoDB on your local machine. ####
 Of course you could modify the code and connect to remote mongo DB, but it preffered to work on local database instance.

### Any links, refference? ###
1. Official [Telegram BOT API](https://core.telegram.org/bots/api)
2. This project using [python-telegram-bot](https://python-telegram-bot.org) as Telegram API wrapper implemenration for this project.
 
 ### What about MongoDB? ###
 * Install [MongoDB](https://www.mongodb.com/download-center/community), and launch it.
 * To work with MongoDB you would need also install [MongoDB Compass](https://www.mongodb.com/download-center/compass) as a GUI for MongoDB. Or you could work in mongo CLI.
 * Create new database with name: FusionClubDB
 * Setup FusionClubDB, how to do that I will describe later.
***
    $ python -m venv virtual_enviroment_folder_name_that_will_be_created
    $ pip install -r requirements.txt
    $ python app.py
