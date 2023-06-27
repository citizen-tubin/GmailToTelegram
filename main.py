from Mail.mail import Mail
from Mail.mail_exception import MailException
from Messaging_app.message_exception import MessageException
from Messaging_app.messaging import Message
import ast
import configparser
import asyncio
import time
import logger
import json

config = configparser.ConfigParser()
config.read('.ini')

is_run_mail_to_whatsapp_job_enabled = config.getboolean('MISSION', 'IS_RUN_MAIL_TO_WHATSAPP_JOB_ENABLED')
is_create_new_filters_enabled = config.getboolean('MAIL.FILTERS', 'IS_CREATE_NEW_FILTERS_ENABLED')
labels_to_filter_by = ast.literal_eval(config.get('MAIL.FILTERS', 'LABELS_TO_FILTER_BY'))
failure_sleeping_time_in_seconds = config.getint('SYSTEM', 'FAILURE_SLEEPING_TIME_IN_SECONDS')
sleeping_time_in_minutes_before_rescanning = config.getint('SYSTEM', 'SLEEPING_TIME_IN_MINUTES_BEFORE_RESCANNING')
scanned_message_label_name = ast.literal_eval(config.get('MAIL', 'SCANNED_MESSAGE_LABEL_NAME'))


async def main():
    while True:
        try:
            message = Message()
            mail = Mail()
            break

        except (MailException, MessageException) as e:
            if isinstance(e, MessageException):
                logger.warning(e)
            elif isinstance(e, MailException):
                await message.send(f"The following error occurred {e}. \n"
                                   f"Please check you mail settings and credentials.")
            else:
                logger.error(e)

            logger.info('System will retry in {} seconds'.format(failure_sleeping_time_in_seconds))
            time.sleep(failure_sleeping_time_in_seconds)

    if is_create_new_filters_enabled:
        mail.create_filters_by_label_info(labels_to_filter_by)

    if is_run_mail_to_whatsapp_job_enabled:
        while True:
            query = init_query()
            summarized_mail = mail.get_mail_summary(query)

            if len(summarized_mail) > 0:
                await message.send(summarized_mail)
                logger.info(f'{len(summarized_mail)} unread mail with provided labels were read.')

            logger.info('The inbox will be rescanned in {} minutes'.format(sleeping_time_in_minutes_before_rescanning))
            time.sleep(sleeping_time_in_minutes_before_rescanning*60)


def init_query():
    keywords_to_search_by = "(" + " OR ".join(['"' + word + '"' for word in labels_to_filter_by]) + ")"
    query = "{} is:unread -label:{}".format(keywords_to_search_by, scanned_message_label_name)

    with open('configs.json', 'r') as file:
        data = json.load(file)
    if data["from_date"] != "":
        query += f" after:{data['from_date']}"
    return query


if __name__ == '__main__':
    logger = logger.app_logger
    asyncio.run(main())
