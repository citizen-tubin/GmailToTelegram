import configparser
import requests
import logger
import ast
from datetime import datetime
from telegram import Bot
from Messaging_app.message_exception import MessageException

config = configparser.ConfigParser()
config.read('.ini')

bot_token = config.get('TELEGRAM', 'TOKEN')
poll_interval_in_hours = config.getint('TELEGRAM', 'POLL_INTERVAL_IN_HOURS')
chat_id_ = ast.literal_eval(config.get('TELEGRAM', 'CHAT_ID'))

logger = logger.app_logger


class Message:
    def __init__(self):
        self.last_token_refresh_datetime = None
        self.__initialize()

    def update_last_token_refresh_time(self):
        self.last_token_refresh_datetime = datetime.now()
        logger.info(f"Token refresh time was updated to {self.last_token_refresh_datetime}")

    async def send(self, messages):
        bot = Bot(token=bot_token)
        for message in messages:
            await bot.send_message(chat_id=ast.literal_eval(config.get('TELEGRAM', 'CHAT_ID')), text=message)

    def __set_chat_id_if_not_exist(self):
        if chat_id_ != '':
            return
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url).json()

        if response['ok'] and response['result'] == []:
            missing_chat_id_msg = 'Chat id is missing. ' \
                                     'Please send your Telegram bot a random message to retrieve it.'
            raise Exception(missing_chat_id_msg)
        if not response['ok'] and response['description'] == 'Unauthorized':
            incorrect_token_msg = 'Your bot token is incorrect'
            logger.error(incorrect_token_msg)
            raise Exception(incorrect_token_msg)

        config.set('TELEGRAM', 'CHAT_ID', str(response['result'][0]['message']['chat']['id']))
        with open('.ini', 'w') as config_file:
            config.write(config_file)

    def __initialize(self):
        try:
            self.__set_chat_id_if_not_exist()
        except Exception as error:
            logger.error(error)
            raise MessageException("Failed to initialize Message app.")
