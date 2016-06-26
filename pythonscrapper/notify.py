import sys
sys.path.append('/usr/local/lib/python3.4/dist-packages')

sys.path.append('/home1/04010/ishwor/.local/lib/python2.6/site-packages')

from twilio.rest import TwilioRestClient
import smtplib
import myconfig


def send_email(subject,body):
    recipient = myconfig.recipient
    gmail_user = myconfig.gmail_user
    gmail_pwd = myconfig.gmail_pwd
    
    FROM = myconfig.FROM
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('-- Successfully sent email notification.')
    except:
        print(sys.exc_info()[0])
        print("-- Failed to send email notification")
        raise

def send_sms(text):
    account_sid = myconfig.account_sid
    auth_token = myconfig.auth_token
    client = TwilioRestClient(account_sid, auth_token)
    sms_recipient = myconfig.sms_recipient
    sms_from = myconfig.sms_from
    for rec in sms_recipient:
        message = client.messages.create(to=rec, from_=sms_from,body=text)
    print("-- Sent sms notification")

def notify_error(date,gameid,url):
    subject = "Error occured while downloading game data"
    message = "Error has occured downloading game for date: "+str(date)+" the gameid: "+str(gameid)+" using url: "+str(url)
    notify_message(message)

def notify_message(subject,message):
	send_email(subject,message)
	#send_sms(message)	

def notify_status(message):
    subject = "Status report for the scrapper"
    notify_message(subject,message)
#notify_message("Hello test")