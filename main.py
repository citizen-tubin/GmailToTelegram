from Mail.mail import Mail
from Messaging_app.messaging import Message
import ast
import configparser
import asyncio


config = configparser.ConfigParser()
config.read('.ini')

is_run_mails_to_whatsapp_job_enabled = config.getboolean('MISSION', 'IS_RUN_MAILS_TO_WHATSAPP_JOB_ENABLED')
is_create_new_filters_enabled = config.getboolean('MAIL.FILTERS', 'IS_CREATE_NEW_FILTERS_ENABLED')
filters_to_create = ast.literal_eval(config.get('MAIL.FILTERS', 'FILTERS_MESSAGE_CONTAINING'))


async def main():
    mail = Mail()
    message = Message()
    if is_create_new_filters_enabled:
        mail.create_filters_by_label_string(filters_to_create)

    if is_run_mails_to_whatsapp_job_enabled:
        summarized_mails = mail.get_mails_with_credentials()

        if len(summarized_mails) > 0:
            await message.send(summarized_mails)
            print('All unread mails with provided labels were read.')

if __name__ == '__main__':
    asyncio.run(main())
