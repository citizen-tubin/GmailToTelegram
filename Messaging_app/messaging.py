import configparser
import requests
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from Messaging_app.message_exception import MessageException

config = configparser.ConfigParser()
config.read('.ini')

bot_token = config.get('TELEGRAM', 'TOKEN')
poll_interval_in_hours = config.getint('TELEGRAM', 'POLL_INTERVAL_IN_HOURS')

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
        return False

    async def send(self, messages):
        bot = Bot(token=bot_token)
        for message in messages:
            await bot.send_message(chat_id=self.chat_id, text=message)

    def __get_chat_id(self):
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url).json()

        if response['ok'] and response['result'] == []:
            raise Exception('New bot token is required. '
                                     'Please send your Telegram bot a random message and rerun program')
        if not response['ok'] and response['description'] == 'Unauthorized':
            raise Exception('Your bot token is incorrect')

        chat_id = response['result'][0]['message']['chat']['id']
        return chat_id

    async def error(self, update:Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} caused error: {context.error}')

    async def __handle_user_response(self, update: Update):
        message_type = update.message.chat.type
        text = update.message.text
        self.last_token_refresh_datetime = datetime.now()
        print(f'User ({update.message.chat.id}) in {message_type} sent message: "{text}". Token is refreshed.')

    def __start_incoming_messages_handler_bot(self):
        print("Starting incoming message bot...")
        app = Application.builder().token(bot_token).build()
        app.add_handler(MessageHandler(filters.TEXT, self.__handle_user_response))
        app.add_error_handler(self.error)

        print("Polling...")
        app.run_polling(poll_interval=5)

    def __initialize(self):
        try:
            self.chat_id = self.__get_chat_id()
            self.__start_incoming_messages_handler_bot()
        except Exception as error:
            print(error)
            raise MessageException("Failed to initialize Message app.")
