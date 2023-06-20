import configparser
import requests
import logger
from datetime import datetime
from telegram import Bot
from Messaging_app.message_exception import MessageException

config = configparser.ConfigParser()
config.read('.ini')

bot_token = config.get('TELEGRAM', 'TOKEN')
poll_interval_in_hours = config.getint('TELEGRAM', 'POLL_INTERVAL_IN_HOURS')

logger = logger.app_logger

class Message:
    def __init__(self):
        self.chat_id = None
        self.last_token_refresh_datetime = None
        self.__initialize()

    def is_refresh_token_required(self):
        # Telegram requires the user to send a message to the bot every 24 hours in order to refresh the token.
        # This app will send a refresh request in smaller intervals in order to keep this service running
        if self.last_token_refresh_datetime is not None:
            time_diff = datetime.now() - self.last_token_refresh_datetime
            diff_in_hours = time_diff.total_seconds() / 3600
            return diff_in_hours >= poll_interval_in_hours
        return True

    def update_last_token_refresh_time(self):
        self.last_token_refresh_datetime = datetime.now()
        logger.info(f"Token refresh time was updated to {self.last_token_refresh_datetime}")

    async def send(self, messages):
        bot = Bot(token=bot_token)
        for message in messages:
            await bot.send_message(chat_id=self.chat_id, text=message)

    def __get_chat_id(self):
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url).json()

        if response['ok'] and response['result'] == []:
            new_token_required_msg = 'New bot token is required. ' \
                                     'Please send your Telegram bot a random message and rerun program'
            raise Exception(new_token_required_msg)
        if not response['ok'] and response['description'] == 'Unauthorized':
            incorrect_token_msg = 'Your bot token is incorrect'
            logger.error(incorrect_token_msg)
            raise Exception(incorrect_token_msg)

        chat_id = response['result'][0]['message']['chat']['id']
        return chat_id

    def __initialize(self):
        try:
            self.chat_id = self.__get_chat_id()
        except Exception as error:
            logger.error(error)
            raise MessageException("Failed to initialize Message app.")
