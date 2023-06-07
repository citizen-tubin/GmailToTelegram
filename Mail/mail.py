import os.path
import base64
import ast
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import configparser

config = configparser.ConfigParser()
config.read('.ini')

scopes = ast.literal_eval(config.get('MAIL', 'SCOPES'))
search_labels = ast.literal_eval(config.get('MAIL', 'SEARCH_LABELS'))
token_path = config.get('MAIL', 'TOKEN_PATH')
credentials_path = config.get('MAIL', 'CREDENTIALS_PATH')
is_mark_as_read_enabled = bool(config.get('MAIL', 'IS_MARK_AS_READ_ENABLED'))
is_add_scanned_label_enabled = bool(config.get('MAIL', 'IS_ADD_SCANNED_LABEL_ENABLED'))


class Mail:
    def __init__(self):
        self.__get_credentials_info()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def get_mails_with_credentials(self, filter_by):
        try:
            messages_meta_data = self.__get_messages_meta_data(filter_by)
            if not messages_meta_data:
                return []

            summarized_messages = []
            for message_meta_data in messages_meta_data:
                message_info = self.service.users().messages().get(userId='me', id=message_meta_data['id']).execute()
                message_summary = {item['name']: item['value'] for item in message_info['payload']['headers']}
                result = self.__convert_to_summary_structure(message_meta_data['id'], filter_by, message_info['snippet'], message_summary)
                self.__mark_message_as_processed(message_meta_data['id'], [filter_by])
                summarized_messages.append(result)
            return summarized_messages
        except Exception as error:
            print(f'An error occurred: {error}')

    async def send(self, sender, recipient, label_name, msg_template):
        return

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

    def __get_messages_meta_data(self, filter_by):
        label_ids = self.get_label_ids()
        query = "is:unread {}".format(filter_by)
        results = self.service.users().messages().list(userId='me', labelIds=label_ids, q=query).execute()
        return results.get('messages', [])

    def get_label_ids(self):
        label_ids = []
        labels = self.service.users().labels().list(userId='me').execute().get('labels', [])

        if not labels or len(labels) == 0:
            pass
        for label in labels:
            if label['name'] in search_labels:
                label_ids.append(label['id'])
        return label_ids

    def __convert_to_summary_structure(self, message_id, filter_by, snippet, message_header):
        return f"Subject:{message_header['Subject']}\n" \
            f"From: {message_header['From']} \n" \
            f"Artist: {filter_by} \n" \
            f"Mail Summary: {snippet} \n" \
            f"Sent At: {message_header['Date']}"

    def __mark_message_as_processed(self, message_id, custom_labels):
        labels_to_add = []
        labels_to_remove = []
        body = {}

        if is_mark_as_read_enabled:
            labels_to_remove.append('UNREAD')
            body['removeLabelIds'] = labels_to_remove

        if is_add_scanned_label_enabled:
            labels_to_add.append('SCANNED')
        if custom_labels and len(custom_labels) > 0:
            labels_to_add.extend(custom_labels)

        # if (len(labels_to_add) > 0): body['addLabelIds'] = labels_to_add #TODO 4

        self.service.users().messages().modify(userId='me', id=message_id,
                                               body=body).execute()
