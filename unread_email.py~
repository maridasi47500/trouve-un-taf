import imaplib, email
import requests
import os
import subprocess
import string
import random
from flask import Flask, render_template, request, session
from werkzeug.utils import secure_filename
import json
import re

from email.header import decode_header
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 
def get_email_body(message):  
    body = []  
    if message.is_multipart():  
        # Iterate over all parts  
        for part in message.walk():  
            content_type = part.get_content_type()  
            # Skip attachments and non-text parts  
            if content_type in ('text/plain', 'text/html'):  
                # Get the payload (body content)  
                payload = part.get_payload(decode=True)  # decode=True handles base64/quoted-printable  
                charset = part.get_content_charset() or 'utf-8'  # Default to utf-8 if charset missing  
                body.append(payload.decode(charset, errors='replace'))  # 'replace' handles encoding errors  
    else:  
        # Non-multipart: payload is the body  
        payload = message.get_payload(decode=True)  
        charset = message.get_content_charset() or 'utf-8'  
        body.append(payload.decode(charset, errors='replace'))  
    return '\n'.join(body)  


app = Flask(__name__)
@app.route("/")
def index():
    try:
        lastemail = int(request.args.get("nbemail"))
        print("option 1", lastemail)
    except:
        lastemail = 10
        print("option 2")
    # accessing and printing value
    print(os.getenv("MY_KEY"))
    
    
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    username=os.getenv("MYEMAIL")
    mail.login(username, os.getenv("MYPASS"))
    mail.select("inbox")
    
    #status, ids = mail.search(None, "UNSEEN")
    status, ids = mail.search(None, "SEEN")
    ids = ids[0].split()[-(lastemail):] if ids[0] else []
    ids.reverse()
    emails=[] 
    for eid in ids:
        status, data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        subject, enc = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(enc or "utf-8", errors="replace")
        print(f"From: {msg['From']}")
        print(f"Subject: {subject}")
        print(f"Date: {msg['Date']}")
        body = get_email_body(msg)  
        #print("Email Body:\n", body)  
        if msg["From"] in ["donotreply@jobalert.indeed.com"]:
            emails.append({"body": body, "from": msg["From"], "subject": subject, "date": msg["Date"]})
    return render_template("index.html", emails=emails, username=username,nbemails=lastemail)

        
    
    mail.logout()
if __name__ == "__main__":
    app.run()
    app.debug = True


