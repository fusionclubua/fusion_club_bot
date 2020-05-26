# Fusion Club Ad Master - Telegram Bot #
## General information ##
Please, join to Telegram Messanger group [Чат бот для Fusion Club](https://t.me/joinchat/A1CpsBikC2CA31ExnyYAGg) if you would like to help or discuss this project.
***
## How to run this bot ##
#### This bot will not work out of box, it require to install MongoDB on your local machine. ####
 Of course you could modify the code and connect to remote mongo DB, but it preffered to work on local database instance.

 ### So you need to: ###
 * Install [MongoDB](https://www.mongodb.com/download-center/community), and launch it.
 * To work with MongoDB you would need also install [MongoDB Compass](https://www.mongodb.com/download-center/compass) as a GUI for MongoDB. Or you could work in mongo CLI.
 * Create new database with name: FusionClubDB
 * Setup FusionClubDB, how to do that I will describe later.
***
    $ python -m venv < venv folder >
    $ pip install -r requirements.txt
    $ python app.py
