import pickle
import os.path
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

import base64
from bs4 import BeautifulSoup

def get_email_body(msg):
    if 'parts' in msg['payload']:
        return get_text_from_parts(msg['payload']['parts'])
    else:
        return get_text_from_part(msg['payload'])

def get_text_from_parts(parts):
    text = ""
    for part in parts:
        if part['mimeType'] == 'text/plain':
            text += get_text_from_part(part)
        elif part['mimeType'] == 'text/html':
            text += get_text_from_html(part)
    return text

def get_text_from_part(part):
    if 'data' in part['body']:
        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    return ""

def get_text_from_html(part):
    html = get_text_from_part(part)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

# Update print_email_details function
def print_email_details(msg):
    headers = msg['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    sender = next(header['value'] for header in headers if header['name'] == 'From')
    body = get_email_body(msg)

    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print(f"Body: {body[:100]}...") # Print first 100 characters of the body
    print("-" * 50)

import os

def save_attachment(service, msg_id, store_dir):
    message = service.users().messages().get(userId='me', id=msg_id).execute()
    for part in message['payload'].get('parts', []):
        if part.get('filename'):
            if 'data' in part['body']:
                data = part['body']['data']
            else:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(userId='me', messageId=msg_id, id=att_id).execute()
                data = att['data']
            
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            
            path = os.path.join(store_dir, part['filename'])
            with open(path, 'wb') as f:
                f.write(file_data)

def fetch_emails(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print_email_details(msg)
        save_attachment(service, message['id'], 'attachments')


def search_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print_email_details(msg)

# Usage example
search_emails(service, "from:example@gmail.com")

def fetch_all_emails(service):
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])
    
    while 'nextPageToken' in results:
        page_token = results['nextPageToken']
        results = service.users().messages().list(userId='me', pageToken=page_token).execute()
        messages.extend(results.get('messages', []))
    
    return messages

# indeed, linkedin, welcome to the jungle, hello work, apec, cadremploi, meteojob, jobleads
