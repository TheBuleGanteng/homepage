import base64
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os
from pathlib import Path
import phonenumbers
from phonenumber_field.phonenumber import to_python
import requests 

# Retrieve the logger configured in settings.py
logger = logging.getLogger(__name__)

# Global variable for email address from which automated emails are sent and received
personal_email_address= os.getenv('PERSONAL_EMAIL_ADDRESS')
info_email_address= os.getenv('INFO_EMAIL_ADDRESS')
dnr_email_address= os.getenv('DNR_EMAIL_ADDRESS')
domain_name= os.getenv('DOMAIN_NAME')


# Generate country code from 2-letter country abbreviation
def get_country_code(country_abbrev):
    try:
        country_abbrev = country_abbrev.upper()  # Ensure uppercase
        country_code = phonenumbers.country_code_for_region(country_abbrev)
        if country_code:
            return '+' + str(country_code)
    except Exception as e:
        # Handle exceptions if necessary
        pass
    return None  # Return None if country code is not found or an error occurs


# To send emails
def send_email(body, recipient, sender, subject):    
    print(f'running send_email ... body is: {body}')
    
    try:
        # Absolute path to the service account file
        SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'gitignored', 'gmail_access_credentials.json')

        # Define the required scope for sending emails
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        # Use the service account to acquire credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Specify the user to impersonate
        user_to_impersonate = 'matt@mattmcdonnell.net'  # Replace with the email of the user you're impersonating

        # Impersonate the user
        credentials = credentials.with_subject(user_to_impersonate)

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        # Create a simple MIMEText email
        email_msg = MIMEText(body)
        email_msg['to'] = recipient  # Replace with the recipient's email address
        email_msg['from'] = sender
        email_msg['subject'] = subject

        # Encode the email message in base64
        encoded_message = base64.urlsafe_b64encode(email_msg.as_bytes()).decode()

        # Create the message body
        message_body = {'raw': encoded_message}

        # Send the email
        message = service.users().messages().send(userId='me', body=message_body).execute()
        print(f"Message Id: {message['id']}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


    """
    try:
        # Absolute path of the service account file
        SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'gitignored', 'gmail_access_credentials.json')
        print(f'SERVICE_ACCOUNT_FILE absolute path: {os.path.abspath(SERVICE_ACCOUNT_FILE)}')

        # Check if the service account file exists and can be opened
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            print('Service account file exists.')
            try:
                with open(SERVICE_ACCOUNT_FILE, 'r') as f:
                    print('Successfully opened service account file.')
            except Exception as e:
                print(f'Error opening service account file: {e}')
        else:
            print('Service account file does not exist at the specified path.')
            logger.error('Service account file does not exist at the specified path.')

        # Current working directory
        print(f'Current working directory: {os.getcwd()}')
        logger.info(f'Current working directory: {os.getcwd()}')

        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        print(f'running send_email ... SCOPES is: { SCOPES }')
        logger.info(f'running send_email ... SCOPES is: { SCOPES }')

        # Now use the source credentials to acquire credentials to impersonate another service account
        credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        print(f'running send_email ... credentials is: { credentials }')
        logger.info(f'running send_email ... credentials is: { credentials }')

        # If you're using domain-wide delegation, specify the user to impersonate
        credentials = credentials.with_subject(personal_email_address)
        print(f'running send_email ... credentials is: { credentials }')
        logger.info(f'running send_email ... credentials is: { credentials }')

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        print(f'running send_email ... service is: { service }')
        logger.info(f'running send_email ... service is: { service }')

        # Create and send email
        email_msg = body
        mime_message = MIMEMultipart()
        mime_message['to'] = f'{recipient}'
        mime_message['from'] = f'{dnr_email_address}'
        mime_message['subject'] = f'{subject}'
        mime_message.attach(MIMEText(email_msg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        try:
            message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
            print(f'Message Id is: { id }')
            logger.info(f'Message Id is: { id }')

        except Exception as e:
            print(f'Failed to send email: {e}')
            logger.error(f'Failed to send email: {e}', exc_info=True)

    except Exception as e:
        print(f'An error occurred in send_email: {e}')
        logger.error(f'An error occurred in send_email: {e}', exc_info=True)
        raise
    """