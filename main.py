import os
from dotenv import load_dotenv
import ssl
from email.message import EmailMessage
import smtplib
import imaplib
import email
import re


def check_email(in_email_address, in_password, in_folder='inbox'):
    """

    Args:
        in_email_address (str):
        in_password (str):
        in_folder (str):

    Returns:

    """

    # TODO: Add response in case error in the loging and download processes
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(in_email_address, in_password)
    mail.list()  # Out: list of "folders" aka labels in gmail.
    mail.select(in_folder)  # connect to inbox.

    result, data = mail.search(None, "ALL")

    ids = data[0]  # los datos son una lista.
    id_list = ids.split()  # IDS es una cadena separada por espacios
    latest_email_id = id_list[-1]  # Obtén el ultimo

    result, data = mail.fetch(latest_email_id, "(RFC822)")  # buscar el cuerpo del correo electrónico (RFC822) para la identificación dada

    raw_email = data[0][1]  # here's the body, which is raw text of the whole email # including headers and alternate payloads

    email_message = email.message_from_string(raw_email.decode('utf-8'))

    # Get the email address clean
    pattern = r'<(.*?)>'
    sender_email = re.findall(pattern, email_message['From'])

    return email_message['Subject'], email_message['Date'], sender_email


def send_email(in_password, in_from, in_to, in_subject, in_body):
    """

    Args:
        in_password (str):
        in_from (str):
        in_to (str):
        in_subject (str):
        in_body (str):

    Returns:

    """

    em = EmailMessage()  # Initilize this variable
    em['From'] = in_from
    em['To'] = in_to
    em['Subject'] = in_subject
    em.set_content(in_body)

    # Initialize the email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(in_from, in_password)
            smtp.sendmail(in_from, in_to, em.as_string())
            smtp.quit()
            return True

    except Exception as err:
        print("ERROR:", err)
        return False


# ------- MAIN -------
# TODO: Add setups options
# TODO: Add whitelist for the allowed email address
# TODO: Add log file
#   TODO: Lock the log file while the script is working
# TODO: Save the last 

# --- Setup ---
setup = {}
setup['loop_time'] = 1  # Refresh time in minutes

# Get the password
load_dotenv()

email_address = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
key_subject = 'myip'

#while True:
#    pass
