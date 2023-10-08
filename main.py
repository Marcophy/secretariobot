"""
Secretario bot project
Marco A. Villena, PhD.
2023
"""

# ****** dunder variables ******
__project_name__ = "SECRETARIOBOT"
__author__ = "Marco A. Villena"
__email__ = "mavillenas@proton.me"
__version__ = "0.2"
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
import json


# ****** Functions ******
def check_email(in_email_address, in_password, in_folder='inbox'):
    """
    Download and return the 'unseen' emails for the designed GMAIL account.

    Args:
        in_email_address (str): Gmail address
        in_password (str): Password of gmail email
        in_folder (str): Email folder where the function search the unseen emails. 'inbox' by default.

    Returns: Return a list with all unseen email found.

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

    except Exception as ferr:
        return False, str(ferr)


def send_email(in_password, in_from, in_to, in_subject, in_body):
    """
    Send an email from the master email address to the desired email account.

    Args:
        in_password (str): Password of the master gmail account.
        in_from (str): Email address of the master gmail account.
        in_to (str): Email address of the receiver.
        in_subject (str): Subject of the email
        in_body (str): Body of the email.

    Returns: Return True if the email was sent successfully. False if there is an error.

    """

    em = EmailMessage()  # Initialize this variable
    em['From'] = in_from
    em['To'] = in_to
    em['Subject'] = in_subject
    em.set_content(in_body)

    # Initialize the email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp_server:
            smtp_server.login(in_from, in_password)
            smtp_server.sendmail(in_from, in_to, em.as_string())
            smtp_server.quit()
            return True

    except Exception as ferr:
        print("ERROR:", ferr)
        return False


def get_public_ip():
    """
    Gets the public IP if the machine by two methods:
        - Using the website https://api64.ipify.org?format=json
        - Using the socket libraries

    Returns: Return a list with the result obtained by both methods.

    """

    try:
        response = requests.get('https://api64.ipify.org?format=json').json()
        from_web = response['ip']
    except requests.exceptions.RequestException as ferr:
        from_web = str(ferr)

    try:
        from_local = socket.gethostbyname(socket.gethostname())
    except socket.gaierror as ferr:
        from_local = str(ferr)

    return [from_web, from_local]


def read_whitelist(in_path):
    """
    Read the whitelist.txt file.

    Args:
        in_path (str): Path of the whitelist.txt file

    Returns: Return a list with all emails addresses read for the whitelist.txt file
    """

    file_list = []
    try:
        with open(in_path, 'r') as file:
            for line in file:
                file_list.append(line.strip())

        return True, file_list
    except FileNotFoundError:
        print('ERROR: File not found!')
        return False, file_list
    except Exception as ferr:
        print('ERROR: ' + str(ferr))
        return False, file_list


def check_whitelist(in_lock, in_email, in_whitelist):
    """
    Check if an email address is in the white-list.

    Args:
        in_lock (bool): Status of the whitelist variable in the setup.
        in_email (str): Email for checking.
        in_whitelist (list): White list.

    Returns: Return True if the email is in the white-list or if the in_lock variable is False. False in other case.

    """
    if in_lock:
        if in_email in in_whitelist:
            return True
        else:
            return False
    else:
        return True


def load_config(in_path):
    """
    Load the setup of the script from config file in JSON format.

    Args:
        in_path (str): Path of the configuration file

    Returns: Return a dict with all setup variables.
    """

    try:
        with open(in_path, 'r') as file:
            config = json.load(file)

        return True, config
    except FileNotFoundError:
        print('ERROR: <config.json> file not found')
        return False, None
    except json.JSONDecodeError as ferr:
        print('ERROR decoding JSON file:', ferr)
        return False, None
    except Exception as ferr:
        print('ERROR:', ferr)
        return False, None


# ****** MAIN ******
exec_control = True  # It will be false if there is any error during the setup

# --- Loading Setup ---
err_control, setup = load_config('config.json')
if not err_control:
    exec_control = False

# --- Get the master email address and password ---
load_dotenv()
email_address = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
if email_address is None or password is None:
    print('ERROR: Impossible load the environment variable.')
    exec_control = False

loop_time = 60 * setup['loop_time']

# Load the white list
if setup['whitelist']:
    err_control, white_list = read_whitelist('whitelist.txt')
    if not err_control:
        exec_control = False
else:
    white_list = []

# Main loop
if exec_control:
    try:
        while True:
            status, output = check_email(email_address, password)
            actions_log = []

            if status:
                if 'NONE' in output:
                    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), '\tNo new emails')
                else:
                    for item in output:
                        if check_whitelist(setup['whitelist'], item['sender'], white_list):
                            # ------ MYIP case
                            # Return the public IP
                            if item['subject'] == 'myip':
                                body = str(get_public_ip())
                                body = body + '\n\nMessage generated by SecretarioBot.'
                                if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                    actions_log.append('<myip> sent to ' + item['sender'])
                                else:
                                    actions_log.append('ERROR sending <myip> to ' + item['sender'])
                            # ------ MELON case
                            # Return an internal Joke
                            elif item['subject'].lower() == 'melon' or item['subject'].lower() == 'melón':
                                body = 'Mas melón eres tu.\n\nMessage generated by SecretarioBot.'
                                if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                    actions_log.append('<melon> sent to ' + item['sender'])
                                else:
                                    actions_log.append('ERROR sending <melon> to ' + item['sender'])
                            # ------ LOOPTIME case
                            # Update the loop time
                            elif 'looptime=' in item['subject']:
                                aux = item['subject'].split('=')
                                aux[1] = aux[1].strip()
                                if aux[1].isdigit() and int(aux[1]) > 1:
                                    setup['loop_time'] = int(aux[1])
                                    loop_time = 60 * setup['loop_time']
                                    body = 'Loop-time updated to ' + str(loop_time) + ' seconds.\n\nMessage generated by SecretarioBot.'
                                    if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                        actions_log.append('Loop-time updated to ' + str(setup['loop_time']) + ' minutes. <looptime> sent to ' + item['sender'])
                                    else:
                                        actions_log.append('Loop-time updated to ' + str(setup['loop_time']) + ' minutes. ERROR sending <looptime> to ' + item['sender'])
                                else:
                                    body = 'ERROR updating the loop-time.'
                                    if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                        actions_log.append('Error in <looptime> sent to ' + item['sender'])
                                    else:
                                        actions_log.append('ERROR sending <looptime> result to ' + item['sender'])
                            # ------ HELP case
                            # Send the help information
                            elif 'help' in item['subject']:
                                body = 'Visit https://github.com/Marcophy/secretariobot for more information.\n\nMessage generated by SecretarioBot.'
                                if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                    actions_log.append('<Help> sent to ' + item['sender'])
                                else:
                                    actions_log.append('ERROR sending <help> result to ' + item['sender'])

                            # ------ UNIDENTIFIED SUBJECT case
                            else:
                                if setup['report_unidentified']:
                                    body = 'The subject ' + item['subject'] + ' could not be identified.\nSend <help> for more information.\n\nMessage generated by SecretarioBot.'
                                    if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                        actions_log.append('Unidentified subject sent to ' + item['sender'])
                                    else:
                                        actions_log.append('ERROR sending unidentified subject to ' + item['sender'])
                                else:
                                    actions_log.append('Unidentified subject sent from ' + item['sender'] + '. NO REPORTED.')
                        else:
                            if setup['report_unidentified']:
                                body = 'Sorry, you do not have access to this system.\n\nMessage generated by SecretarioBot.'
                                if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                    actions_log.append('WARNING: ' + item['sender'] + ' is not in white-list. This issue was reported to the sender.')
                                else:
                                    actions_log.append('WARNING: ' + item['sender'] + ' is not in white-list. ERROR reporting this issue to the sender.')
                            else:
                                actions_log.append('WARNING: ' + item['sender'] + ' is not in white-list. NO REPORTED.')

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
else:
    print('Sorry! Something was wrong and I cannot continue.')
