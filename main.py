from Mail.mail import Mail
from Mail.mail_exception import MailException
from Messaging_app.message_exception import MessageException
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
failure_sleeping_time_in_seconds = config.getint('SYSTEM', 'FAILURE_SLEEPING_TIME_IN_SECONDS')
sleeping_time_in_minutes_before_rescanning = config.getint('SYSTEM', 'SLEEPING_TIME_IN_MINUTES_BEFORE_RESCANNING')

async def main():
    while True:
        try:
            mail = Mail()
            message = Message()
            break
        except (MailException, MessageException) as e:
            if isinstance(e, MailException) or isinstance(e, MessageException):
                print(e)
            else:
                print('An unexpected exception occurred.')
            print('System will retry in {} seconds'.format(failure_sleeping_time_in_seconds))
            time.sleep(failure_sleeping_time_in_seconds)


    if is_create_new_filters_enabled:
        mail.create_filters_by_label_name(labels_to_filter_by)

    if is_run_mail_to_whatsapp_job_enabled:
        while True:
            summarized_mail = mail.get_mail_with_credentials()

            if len(summarized_mail) > 0:
                await message.send(summarized_mail)
                print('All unread mail with provided labels were read.')

            print('The inbox will be rescanned in {} minutes'.format(sleeping_time_in_minutes_before_rescanning))
            time.sleep(failure_sleeping_time_in_seconds*60)




if __name__ == '__main__':
    asyncio.run(main())




