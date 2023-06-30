    GMAIL:
        1. Go to the Google Cloud Console and sign in with your Google account.
    
        2. Create a new project by clicking on the project dropdown at the top of the screen and selecting "New Project".
    
        3. Give your project a name and click "Create".
    
        4. Once the project is created, select the project from the dropdown at the top of the screen.
    
        5. Enable the Gmail API for your project by clicking on the "Enable APIs and Services" button at the top of the screen,
            then searching for "Gmail API" and selecting it, and finally clicking the "Enable" button.
    
        6. Create a set of OAuth 2.0 credentials: Go to 'Navigation Menu'. Click 'API & Services', on the left handside of screen, and then 'Credentials'. Click "Create credentials", and then select "OAuth client ID":
            6.1 Go to the Google Cloud Console and select your project.
            6.2 In the left-hand navigation menu, select "APIs & Services" > "Credentials".
            6.3 Select the application type you need (e.g., desktop app, web application, etc.) and give your credentials a name.
            6.4 When your application requests authorization from the user, it should launch the user's default web browser 
                and direct them to the authorization URL for the Gmail API. The URL should look something like this:
                
                'https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob'
    
        7. In the "Credentials" section of your project, find the newly created credentials and click on the download button to download the JSON file containing your client ID and secret.
    
    
        8. Save it to the same directory as the script.
    
        9. Rename the credentials file to "credentials.json".
    
        10. In 'Google Cloud Console', go to 'APIs & Services' -> 'OAuth consent screen' -> 'Test users' section -> '+ ADD USERS'. 
            Add Gmail users that could access your Gmail accounts (Gmail, docs).
            Please notice - you still required to insert your own Gmail account even if you logged in with it to 'Google Cloud'
    
    TELEGRAM:
        1. Open your telegram app and search for BotFather. (A built-in Telegram bot that helps users create custom Telegram bots)
        
        2. Type /newbot to create a new bot

        3. Give your bot a name & a username

        4. Send you Telegram bot a random message. Without sending any message, you would not be able to retrive data
            in this script

        5. Copy your new Telegram bot’s token

        
    Python
        1. Download Pycharm and Python 3.9

        2. Run in Terminal 'pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib google-auth python-telegram-bot, pytz'
    
        3. Run the script