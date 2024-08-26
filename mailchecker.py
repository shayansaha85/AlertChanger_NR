import imaplib
from email.header import decode_header

IMAP_SERVER = 'outlook.office365.com'
EMAIL_ACCOUNT = 'shayan851997@outlook.com'
PASSWORD = '*****'
SENDER_EMAIL = 'shayan851997@gmail.com'
SUBJECT_KEYWORD = 'TESTING ALERT CLOSURE | NEW RELIC'

def check_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, PASSWORD)
    mail.select('inbox')

    status, messages = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}" SUBJECT "{SUBJECT_KEYWORD}")')
    email_ids = messages[0].split()
    if email_ids:
        first_email_id = email_ids[0]
        mail.store(first_email_id, '+FLAGS', '\\Seen')
        mail.logout()
        return True
    else:
        mail.logout()
        return False
