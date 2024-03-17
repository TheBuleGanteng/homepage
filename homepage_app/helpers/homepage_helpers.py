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


# Global variable for email address from which automated emails are sent and received
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
    
    # Load service account credentials
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'gitignored', 'gmail_access_credentials.json')
    print(f'running send_email ... SERVICE_ACCOUNT_FILE is: { SERVICE_ACCOUNT_FILE }')

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    print(f'running send_email ... SCOPES is: { SCOPES }')

    # Now use the source credentials to acquire credentials to impersonate another service account
    credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    print(f'running send_email ... credentials is: { credentials }')

    # If you're using domain-wide delegation, specify the user to impersonate
    credentials = credentials.with_subject(dnr_email_address)
    print(f'running send_email ... credentials is: { credentials }')

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=credentials)
    print(f'running send_email ... service is: { service }')

    # Create and send email
    email_msg = body
    mime_message = MIMEMultipart()
    mime_message['to'] = f'{recipient}'
    mime_message['from'] = f'{dnr_email_address}'
    mime_message['subject'] = f'{subject}'
    mime_message.attach(MIMEText(email_msg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print('Message Id: %s' % message['id'])