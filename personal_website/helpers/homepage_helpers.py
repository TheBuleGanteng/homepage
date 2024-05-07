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
PROJECT_NAME= os.getenv('PROJECT_NAME')


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
        SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gitignored', 'gmail_access_credentials.json')

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
