"""
Secretario bot project
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "SECRETARIOBOT"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.1"
__project_date__ = '2023'

# ****** Modules ******
import os
from dotenv import load_dotenv
import ssl
from email.message import EmailMessage
import smtplib
import imaplib
import email
import re
import requests
import socket
from datetime import datetime
import time


# ****** Functions ******
def check_email(in_email_address, in_password, in_folder='inbox'):
    """

    Args:
        in_email_address (str):
        in_password (str):
        in_folder (str):

    Returns:

    """

    pattern = r'<(.*?)>'  # Pattern for sender email cleaning

    try:
        connection = imaplib.IMAP4_SSL('imap.gmail.com')
        connection.login(in_email_address, in_password)
        connection.list()  # Out: list of "folders" aka labels in gmail.
        connection.select(in_folder)  # connect to inbox.

        status, email_ids = connection.search(None, "UNSEEN")

        if email_ids[0]:
            email_ids = email_ids[0].split()
            no_read_emails = []

            for email_id in email_ids:
                status, data = connection.fetch(email_id, "(RFC822)")
                email_string = email.message_from_bytes(data[0][1])

                aux = re.findall(pattern, email_string['From'])

                no_read_emails.append({
                    'subject': email_string['Subject'],
                    'sender': re.findall(pattern, email_string['From'])[0],
                    'date': email_string["Date"]
                })

            connection.logout()
            return True, no_read_emails
        else:
            connection.logout()
            return True, 'NONE'

    except Exception as err:
        return False, str(err)


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

    em = EmailMessage()  # Initialize this variable
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


def get_public_ip():
    """

    Returns:

    """

    try:
        response = requests.get('https://api64.ipify.org?format=json').json()
        from_web = response['ip']
    except requests.exceptions.RequestException as err:
        from_web = str(err)

    try:
        from_local = socket.gethostbyname(socket.gethostname())
    except socket.gaierror as err:
        from_local = str(err)

    return [from_web, from_local]


# ****** MAIN ******
# TODO: Add setups options
# TODO: Add whitelist for the allowed email address
# TODO: Add the HELP email
# TODO: Add log file
#   TODO: Lock the log file while the script is working

# --- Setup ---
setup = {
    'loop_time': 1,                 # Cycle time in minutes
    'log_file': False,              # Enable/disable log file
    'whitelist': True,              # Enable/disable the filter by white-list
    'report_unidentified': True     # Enable/disable the authomatic answer if the subject is not identified
}

# Get the password
load_dotenv()

email_address = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
loop_time = 60 * setup['loop_time']

# Main loop
try:
    while True:
        status, output = check_email(email_address, password)
        actions_log = []

        if status:
            if 'NONE' in output:
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\tNo new emails')
            else:
                for item in output:
                    # ------ MYIP case
                    if item['subject'] == 'myip':
                        body = str(get_public_ip())
                        if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                            actions_log.append('<myip> sent to ' + item['sender'])
                        else:
                            actions_log.append('ERROR sending <myip> to ' + item['sender'])
                    # ------ MELON case
                    elif item['subject'] == 'melon' or item['subject'] == 'melón':
                        body = 'Mas melón eres tu.'
                        if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                            actions_log.append('<melon> sent to ' + item['sender'])
                        else:
                            actions_log.append('ERROR sending <melon> to ' + item['sender'])
                    # ------ UNIDENTIFIED SUBJECT case
                    else:
                        if setup['report_unidentified']:
                            body = 'The subject ' + item['subject'] + ' could not be identified.\nSend <help> for more information.'
                            if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                actions_log.append('Unidentified subject sent to ' + item['sender'])
                            else:
                                actions_log.append('ERROR sending unidentified subject to ' + item['sender'])

                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\t' + '; '.join(actions_log))
        else:
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\tERROR: ' + output)

        time.sleep(loop_time)

except KeyboardInterrupt:
    print('Script stopped by Ctrl+c')

except Exception as err:
    print('ERROR:', err)

finally:
    print('END')
