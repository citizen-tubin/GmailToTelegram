import configparser
import requests
from telegram import Bot

config = configparser.ConfigParser()
config.read('.ini')

bot_token = config.get('TELEGRAM','TOKEN')


class Message:
    def __init__(self):
        self.chat_id = self.__get_chat_id()

    async def send(self, messages):
        for message in messages:
            bot = Bot(token=bot_token)
            await bot.send_message(chat_id=self.chat_id, text=message)


    def __get_chat_id(self):
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response =  requests.get(url).json()
        if response['ok'] == True and response['result'] == []:
            print ('New bot token is required. Please send your Telegram bot a random message and rerun program')
            print ('Stopping the code execution')
            raise SystemExit
        chat_id = response['result'][0]['message']['chat']['id']
        return chat_id
