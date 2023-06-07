from Mail.mail import Mail
import configparser

config = configparser.ConfigParser()
config.read('.ini')

send_label_test_to = config.get('LABEL_TEST','SEND_LABEL_TEST_TO')

def test_labels(mail:Mail):
    #print(f'Following labels were not attached to Mail: {mail_without_labels}')
    return

    # label_ids = Mail.get_label_ids()
    # Mail.send(send_label_test_to, "This is a label test")
    # asyncio.run(send_emails())


