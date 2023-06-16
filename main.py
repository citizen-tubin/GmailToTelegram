from Mail.mail import Mail
from Mail.mail_exception import MailException
from Messaging_app.message_exception import MessageException
from Messaging_app.messaging import Message
import ast
import configparser
import asyncio
import time
from datetime import datetime

config = configparser.ConfigParser()
config.read('.ini')

is_run_mail_to_whatsapp_job_enabled = config.getboolean('MISSION', 'IS_RUN_MAIL_TO_WHATSAPP_JOB_ENABLED')
is_create_new_filters_enabled = config.getboolean('MAIL.FILTERS', 'IS_CREATE_NEW_FILTERS_ENABLED')
labels_to_filter_by = ast.literal_eval(config.get('MAIL.FILTERS', 'LABELS_TO_FILTER_BY'))
failure_sleeping_time_in_seconds = config.getint('SYSTEM', 'FAILURE_SLEEPING_TIME_IN_SECONDS')
sleeping_time_in_minutes_before_rescanning = config.getint('SYSTEM', 'SLEEPING_TIME_IN_MINUTES_BEFORE_RESCANNING')


async def main():
    while True:
        try:
            mail = Mail()
            message = Message()
            break

        except (MailException, MessageException) as e:
            if isinstance(e, MailException):
                print(e)
                await message.send(f"The following error occurred {e}. \n"
                                   f"Please check you mail settings and credentials.")
            if isinstance(e, MessageException):
                print(e)
            else:
                print('An unexpected exception occurred.')

            print('System will retry in {} seconds'.format(failure_sleeping_time_in_seconds))
            time.sleep(failure_sleeping_time_in_seconds)

    await refresh_token_if_required(message)

    if is_run_mail_to_whatsapp_job_enabled:
        while True:
            await refresh_token_if_required(message)
            summarized_mail = mail.get_mail()

            if len(summarized_mail) > 0:
                await message.send(summarized_mail)
                print('All unread mail with provided labels were read.')

            print('The inbox will be rescanned in {} minutes'.format(sleeping_time_in_minutes_before_rescanning))
            time.sleep(sleeping_time_in_minutes_before_rescanning*60)

async def refresh_token_if_required(message):
    if message.is_refresh_token_required():
        await message.send(["To refresh the token, please reply with any message."])
        message.update_last_token_refresh_time()

if __name__ == '__main__':
    asyncio.run(main())
