import os
import traceback
# Please add your own config.py file to override this,
# It can override only Settings class fields
# config.py example:
#config = {
#    'db_bot' : 'bon_name_in_db',
#    'use_webhook': False,
#    'webhook_url': 'http://localhost:443/bot_hook'
#}
# And put this config.py in working dir

#This class contains only default values
class Settings(object):
    def __init__(self):
        self.db_bot    = 'FusionClubADMaster'
        self.use_webhook = False
        self.listen_addr = '0.0.0.0'
        self.listen_port = 8080
        self.webhook_key = "private.pem"
        self.webhook_crt = "public.crt"
        self.url_path = 'bot'
        self.webhook_url = f'http://{self.listen_addr}:{self.listen_port}/bot'
        self.db_name = 'FusionClubDB'
        self.db_address = '127.0.0.1'
        self.db_port = 27017 #MongoDB

        config_file = 'config'
        if os.path.exists(f"{os.getcwd()}/{config_file}.py"):
            custom = __import__(config_file).config
            for key in custom:
                if key in self.__dict__:
                    self.__dict__[key] = custom[key]
                else:
                    raise Exception(f'Unknown settings key in {config_file}.py')


    def get(self, option):
        assert option in self.__dict__.keys(), ("Only Settings class field names allowed to use in this method")
        return self.__dict__.get(option)

settings = Settings()