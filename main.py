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

    except Exception as ferr:
        print("ERROR:", ferr)
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


def read_withelist(in_path):
    """

    Args:
        in_path (str):

    Returns:

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

    Args:
        in_lock (bool):
        in_email (str):
        in_whitelist (list):

    Returns:

    """
    if in_lock:
        if in_email in in_whitelist:
            return True
        else:
            return False
    else:
        return True


def read_help_template(in_path):
    """

    Args:
        in_path (str):

    Returns:

    """

    try:
        with open(in_path, 'r') as file:
            all_lines = file.readlines()

        all_lines = ''.join(all_lines)

        return True, all_lines
    except FileNotFoundError:
        print('ERROR: Help file not found!')
        all_lines = 'none'
        return False, all_lines
    except Exception as ferr:
        print('ERROR: ' + str(ferr))
        all_lines = 'none'
        return False, all_lines


def load_config(in_path):
    """

    Args:
        in_path (str):

    Returns:

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
    print('ERROR: Impossible load the enviroment variable.')
    exec_control = False

loop_time = 60 * setup['loop_time']

# Load the white list
if setup['whitelist']:
    err_control, white_list = read_withelist('whitelist.txt')
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
                                if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                    actions_log.append('<myip> sent to ' + item['sender'])
                                else:
                                    actions_log.append('ERROR sending <myip> to ' + item['sender'])
                            # ------ MELON case
                            # Return a Joke
                            elif item['subject'] == 'melon' or item['subject'] == 'melón':
                                body = 'Mas melón eres tu.\nMas melon eres tu.'
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
                                    body = 'Loop-time updated to ' + str(loop_time) + ' seconds.'
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
                                err_help, help_body = read_help_template('help.txt')
                                if err_help:
                                    if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], help_body):
                                        actions_log.append('<Help> sent to ' + item['sender'])
                                    else:
                                        actions_log.append('ERROR sending <help> result to ' + item['sender'])

                            # ------ UNIDENTIFIED SUBJECT case
                            else:
                                if setup['report_unidentified']:
                                    body = 'The subject ' + item['subject'] + ' could not be identified.\nSend <help> for more information.'
                                    if send_email(password, email_address, item['sender'], 'RE: ' + item['subject'], body):
                                        actions_log.append('Unidentified subject sent to ' + item['sender'])
                                    else:
                                        actions_log.append('ERROR sending unidentified subject to ' + item['sender'])
                                else:
                                    actions_log.append('Unidentified subject sent from ' + item['sender'] + '. NO REPORTED.')
                        else:
                            if setup['report_unidentified']:
                                body = 'Sorry, you do not have access to this system.'
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
