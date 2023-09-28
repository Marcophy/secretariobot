import os
from dotenv import load_dotenv
import imaplib
import email
from email.header import decode_header


load_dotenv()
password = os.getenv("PASSWORD")

try:
    connection = imaplib.IMAP4_SSL('imap.gmail.com')
    connection.login('secretariobot@gmail.com', password)
    connection.list()  # Out: list of "folders" aka labels in gmail.
    connection.select("inbox")  # connect to inbox.

    status, email_ids = connection.search(None, "UNSEEN")

    print('data =', len(email_ids))

    if email_ids[0]:
        email_ids = email_ids[0].split()
        no_read_emails = []

        for email_id in email_ids:
            status, data = connection.fetch(email_id, "(RFC822)")
            email_string = email.message_from_bytes(data[0][1])
            subject, _ = decode_header(email_string['Subject'])[0]
            remitente, _ = decode_header(email_string.get("From", ""))[0]
            date = email_string["Date"]

            no_read_emails.append({
                'subject': subject,
                'from': remitente,
                'date': date
            })

    connection.logout()


except Exception as err:
    print(err)


print('END')
