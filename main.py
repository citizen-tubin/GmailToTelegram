from Mail.mail import Mail
from Messaging_app.messaging import Message
import ast
import configparser
import asyncio
import time

config = configparser.ConfigParser()
config.read('.ini')

is_run_mail_to_whatsapp_job_enabled = config.getboolean('MISSION', 'IS_RUN_MAIL_TO_WHATSAPP_JOB_ENABLED')
is_create_new_filters_enabled = config.getboolean('MAIL.FILTERS', 'IS_CREATE_NEW_FILTERS_ENABLED')
labels_to_filter_by = ast.literal_eval(config.get('MAIL.FILTERS', 'LABELS_TO_FILTER_BY'))
sleeping_time_in_seconds = config.getint('SYSTEM', 'SLEEPING_TIME_IN_SECONDS')

async def main():
    while True:
        try:
            mail = Mail()
            message = Message()
            break
        except Exception as e:
            print('Failure occurred. System will retry in {} seconds'.format(sleeping_time_in_seconds))
            time.sleep(sleeping_time_in_seconds)


    if is_create_new_filters_enabled:
        mail.create_filters_by_label_string(labels_to_filter_by)

    if is_run_mail_to_whatsapp_job_enabled:
        summarized_mail = mail.get_mail_with_credentials()

        if len(summarized_mail) > 0:
            await message.send(summarized_mail)
            print('All unread mail with provided labels were read.')

if __name__ == '__main__':
    asyncio.run(main())




