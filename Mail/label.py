
def create_label_if_not_exist(service, label_to_add):

    existing_labels = service.users().labels().list(userId='me').execute()
    existing_label_names = {label['name'] for label in existing_labels['labels']}

    if label_to_add not in existing_label_names:
        new_label = {
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'name': label_to_add
        }
        created_label = service.users().labels().create(userId='me', body=new_label).execute()
        print(f"Label '{label_to_add}' created with ID: {created_label['id']}")
        return {'id':created_label['id'],'name':created_label['name'],'is_already_exists':False}
    else:
        print(f"Label '{label_to_add}' already exists")
        existing_label = next((obj for obj in existing_labels['labels'] if obj['name'] == label_to_add), None)
        existing_label['is_already_exists'] = True
        return existing_label




