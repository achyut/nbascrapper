from twilio.rest import TwilioRestClient
import smtplib
import myconfig
import sys

def send_email(body):
    recipient = myconfig.recipient
    gmail_user = myconfig.gmail_user
    gmail_pwd = myconfig.gmail_pwd
    
    FROM = myconfig.FROM
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = "Error occured while downloading game data"
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
	message = "Error has occured downloading game for date: "+date+" the gameid: "+str(gameid)+" using url: "+url
	notify_message(message)

def notify_message(message):
	send_email(message)
	#send_sms(message)	

notify_message("Hello test")