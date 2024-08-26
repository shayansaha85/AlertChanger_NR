import pandas as pd
import requests
import os
import configparser
import imaplib
from email.header import decode_header
from apscheduler.schedulers.blocking import BlockingScheduler


# INPUT DATA
ALERT_SHOULD_BE = 'true'
IMAP_SERVER = 'outlook.office365.com'
EMAIL_ACCOUNT = 'shayan851997@outlook.com'
PASSWORD = '******'
SENDER_EMAIL = 'shayan851997@gmail.com'
SUBJECT_KEYWORD_ENABLE = 'TESTING ALERT ENABLE | NEW RELIC'
FOLDERNAME = 'alertman'
CONDITION_ID_SHEET_PATH = './conditionID.csv'

def ENABLE_ALERTS():
    def alert_disable_email_received(foldername):
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        mail.select(foldername)

        status, messages = mail.search(None, f'(UNSEEN FROM "{SENDER_EMAIL}" SUBJECT "{SUBJECT_KEYWORD_ENABLE}")')
        email_ids = messages[0].split()
        if email_ids:
            first_email_id = email_ids[0]
            mail.store(first_email_id, '+FLAGS', '\\Seen')
            mail.logout()
            return True
        else:
            mail.logout()
            return False


    # Reading config file to fetch endpoint, account ID and API Key for New Relic API call
    config = configparser.ConfigParser()
    config.read('config.ini')
    endpoint = config.get('settings', 'endpoint')
    accountID = config.get('settings', 'accountID')
    apikey = config.get('settings', 'apikey')
    data = pd.read_csv(CONDITION_ID_SHEET_PATH)
    conditionIDs = list(data["conditionIDs"])


    # Method for disabling NRQL baseline alerts
    def disableAlertsBaseline(condition):
        url = str(endpoint)
        query = '''
        mutation {
        alertsNrqlConditionBaselineUpdate(
            accountId: ''' + str(accountID) + '''
            id: "''' + str(condition) + '''"
            condition: {
            enabled: ''' + ALERT_SHOULD_BE + '''
            }
            ) {
                id
            }
            }
        '''
        headers = {
            'Content-Type': 'application/json',
            'API-Key': str(apikey)
        }
        payload = {
            'query': query
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            pass
        else:
            print(f"Error: {response.status_code}")
            print(response.text)



    # Method for disabling NRQL static alerts

    def disableAlertsStatic(condition):
        url = 'https://api.newrelic.com/graphql'
        query = '''
            mutation {
            alertsNrqlConditionStaticUpdate(
                accountId: ''' + str(accountID) + '''
                id: "''' + str(condition) + '''"
                condition: {
                enabled: ''' + ALERT_SHOULD_BE + '''
                }
            ) {
                id
            }
            }
            '''
        headers = {
            'Content-Type': 'application/json',
            'API-Key': str(apikey)
        }
        payload = {
            'query': query
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            pass

        else:
            print(f"Error: {response.status_code}")
            print(response.text)


    if alert_disable_email_received(FOLDERNAME):
        print()
        print("EMAIL FOR ENABLING ALERTS IS RECEIVED")
        for condition in conditionIDs:
            disableAlertsBaseline(condition)
            disableAlertsStatic(condition)
            print(f">> Alert Enabled For {condition}")
        print()
        print("------ WORK DONE ------")
        print()
    else:
        print("EMAIL NOT RECEIVED FOR ENABLING THE ALERTS")

scheduler = BlockingScheduler()
scheduler.add_job(ENABLE_ALERTS, 'interval', seconds = 5)
scheduler.start()

