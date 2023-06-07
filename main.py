from Mail.mail import Mail
from Messaging_app.messaging import Message
import ast
import configparser
import asyncio

from Mail.test_labels import test_labels

config = configparser.ConfigParser()
config.read('.ini')

search_in_message = ast.literal_eval(config.get('MAIL','SEARCH_IN_MESSAGE'))
run_mails_to_whatsapp_job = bool(config.get('MISSION','RUN_MAILS_TO_WHATSAPP_JOB'))
run_test_if_labels_work_job = bool(config.get('MISSION','RUN_TEST_IF_LABELS_WORK_JOB'))


async def main():
    mail = Mail()
    message = Message()
    if run_mails_to_whatsapp_job:
        summarized_mails = [mail.get_mails_with_credentials(item) for item in search_in_message]

        if len(summarized_mails) > 0:
            await message.send(summarized_mails)
            print('All unread mails with provided labels were read.')

    if run_test_if_labels_work_job:
        test_labels(mail)
        print("'test labels' process finished.")


if __name__ == '__main__':
    asyncio.run(main())