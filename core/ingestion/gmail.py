import imaplib
import email
import os
import uuid
import logging
from email import generator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

user = 'mukadam.kausar@gmail.com'
# App password generated from gmail.
password = 'tehkznrndrjgvqzo'
imap_url = 'imap.gmail.com'
data_len = 10


# Get content body from email. For simplicity, we try to skip any non-text content.
def get_body(parsed_email, decode):
    body = ""
    if parsed_email.is_multipart():
        for part in parsed_email.walk():
            content_type = part.get_content_type()
            content_dispo = str(part.get('Content-Disposition'))
            # Skip any text/plain (txt) attachments for simplicity.
            if content_type == 'text/plain' and 'attachment' not in content_dispo:
                body = part.get_payload(decode=decode)  # decode
    # Not multipart - i.e. plain text, no attachments
    else:
        body = parsed_email.get_payload(decode=decode)
    return body

def trim(email, decode=True):
    msg = MIMEMultipart()
    msg["To"] = email["To"]
    msg["From"] = email["From"]
    msg["Subject"] = email["Subject"]

    if email.is_multipart():
        for part in email.walk():
            content_type = part.get_content_type()
            if content_type == 'text/html':
                text = part.get_payload(decode=decode)
                msg.attach(MIMEText(text.decode(errors='replace'), 'html'))
                return msg
    return None

# Retrieve message content for emails listed.
def get_emails(message_ids, limit=None):
    msgs = []  # all the email data are pushed inside an array
    for index, num in enumerate(message_ids[0].split()):
        typ, data = con.fetch(num, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                # Get email content & metadata.
                msgs.append(email.message_from_bytes(response_part[1]))
        if limit is not None and index >= limit - 1:
            break
    return msgs

# Store email body to disk for indexing.
def store_to_file(emails, path):
    os.chdir(path)
    def write_eml_file(msg):
        filename = str(uuid.uuid4()) + ".eml"
        trimmed = trim(msg)
        if trimmed is not None:
            with open(filename, 'w') as file:
                emlGenerator = generator.Generator(file)
                emlGenerator.flatten(trimmed)
        else:
            logging.warning("Skipping email since no text/html body was found.")


    for email in emails:
        write_eml_file(email)


# Setup SSL connection with gmail & login user.
con = imaplib.IMAP4_SSL(imap_url)
con.login(user, password)
print("User logged in successfully!")
print()

# Get all unseen emails for indexing.
con.select('Inbox')
query = '(UNSEEN)'  # For retrieving only unseen messages. Sometimes this might not have enough data to build a model.
retcode, message_ids = con.search(None, query)
filepath = "../../data/raw_data"
if retcode == 'OK':
    print('Retrieved message ids!')
    print()

    emails = get_emails(message_ids, limit=data_len)
    print("Retrieved messages!")
    print()

    store_to_file(emails, filepath)
    print("Emails stored for indexing!")
