import os.path
import ast
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import configparser

from Mail.mail_exception import MailException

config = configparser.ConfigParser()
config.read('.ini')

scopes = ast.literal_eval(config.get('MAIL', 'SCOPES'))
scanned_message_label = ast.literal_eval(config.get('MAIL', 'SCANNED_MESSAGE_LABEL'))
token_path = config.get('MAIL', 'TOKEN_PATH')
credentials_path = config.get('MAIL', 'CREDENTIALS_PATH')
is_mark_as_read_enabled = config.getboolean('MAIL', 'IS_MARK_AS_READ_ENABLED')
labels_to_filter_by = ast.literal_eval(config.get('MAIL.FILTERS', 'LABELS_TO_FILTER_BY'))

class Mail:
    def __init__(self):
        self.creds = ""
        self.service = ""
        self.labels_info = []
        self.labels_names = []
        self.__initialize()

    def create_label_if_not_exist(self, label_to_add):

        if label_to_add not in self.labels_names:
            new_label = {
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
                'name': label_to_add
            }
            created_label = self.service.users().labels().create(userId='me', body=new_label).execute()
            print(f"Label '{label_to_add}' created with ID: {created_label['id']}")
            return created_label
        else:
            print(f"Label '{label_to_add}' already exists")
            existing_label = next((obj for obj in self.labels_info['labels'] if obj['name'] == label_to_add), None)
            return existing_label

    def get_labels_names(self):
        self.labels_info = self.service.users().labels().list(userId='me').execute()
        self.labels_names = [label['name'] for label in self.labels_info['labels']]

    def create_filters_by_label_name(self, names):
        filter_criteria = {
            'criteria': {
                'query': ''
            },
            'action': {
                'addLabelIds': [],
                'removeLabelIds': [],
                'markImportant': True,
                'neverSpam': True
            },
            'actionName': 'CUSTOM',
            'shouldArchive': False,
            'hasUserLabel': False,
            'category': 'CATEGORY_PERSONAL'
        }

        for name in names:
            if name in self.labels_names:
                continue
            label_info = self.create_label_if_not_exist(name)
            filter_criteria['action']['addLabelIds'] = label_info['id']
            filter_criteria['criteria']['query'] = label_info['name']
            try:
                self.service.users().settings().filters().create(userId='me', body=filter_criteria).execute()
                print(f'Filter {name} created successfully.')
            except Exception as error:
                print(f'An error occurred: {error}')
                raise Exception

    def get_mail_with_credentials(self):
        try:
            messages_meta_data = self.__get_messages_meta_data()
            if not messages_meta_data:
                return []

            summarized_messages = []
            for message_meta_data in messages_meta_data:
                message_info = self.service.users().messages().get(userId='me', id=message_meta_data['id']).execute()
                message_headers = {item['name']: item['value'] for item in message_info['payload']['headers']}
                result = self.__convert_to_summary_structure(message_info['snippet'], message_headers)
                self.__mark_message_as_scanned(message_meta_data['id'])
                summarized_messages.append(result)
            return summarized_messages
        except Exception as error:
            print(f'An error occurred: {error}')
            raise Exception

    def __get_credentials_info(self):
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, scopes)
        is_refresh_required = self.creds and self.creds.expired and self.creds.refresh_token
        is_refresh_error_occurred = False
        if not self.creds or not self.creds.valid:
            if is_refresh_required:
                try:
                    print("Please grant permissions once again for reading and editing Mail.")
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    is_refresh_error_occurred = True
            if not is_refresh_required or is_refresh_error_occurred:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
                self.creds = flow.run_local_server(port=0)

            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

    def __get_messages_meta_data(self):
        keywords_to_search_by = "(" + " OR ".join(['"' + word + '"' for word in labels_to_filter_by]) + ")"
        query = "{} is:unread -label:{}".format(keywords_to_search_by , scanned_message_label)
        results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()
        return results.get('messages', [])

    def __convert_to_summary_structure(self, snippet, message_header):
        return f"Subject:{message_header['Subject']}\n" \
            f"From: {message_header['From']} \n" \
            f"Artist: {''} \n" \
            f"Mail Summary: {snippet} \n" \
            f"Sent At: {message_header['Date']}"

    def __mark_message_as_scanned(self, message_id):
        labels_to_remove = []
        body = {}

        if is_mark_as_read_enabled:
            labels_to_remove.append('UNREAD')
            body['removeLabelIds'] = labels_to_remove
        scanned_label_info = next((obj for obj in self.labels_info['labels'] if obj['name'] == scanned_message_label), None)
        body['addLabelIds'] = [scanned_label_info['id']]

        self.service.users().messages().modify(userId='me', id=message_id,
                                               body=body).execute()

    def __initialize(self):
        try:
            self.__get_credentials_info()
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.get_labels_names()
            self.create_label_if_not_exist(scanned_message_label)
        except MailException as error:
            print(f'An error occurred: {error}')
            raise MailException("Failed to initialize mail.")
