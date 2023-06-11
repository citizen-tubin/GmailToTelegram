from Mail.label import create_label_if_not_exist


def create_filters(service, names):
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
        label_info = create_label_if_not_exist(service, name)
        if not label_info['is_already_exists']:
            filter_criteria['action']['addLabelIds'] = label_info['id']
            filter_criteria['criteria']['query'] = label_info['name']
            try:
                service.users().settings().filters().create(userId='me', body=filter_criteria).execute()
                print(f'Filter {name} created successfully.')
            except Exception as error:
                print(f'An error occurred: {error}')
                raise SystemExit
