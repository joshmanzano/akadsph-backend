import smtplib
from multiprocessing import Lock
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import os

# reading .env file


gmail_user = 'akads.noreply@gmail.com'
gmail_password = '1akadsph!'
lock = Lock()

def load_template():
    with open('templates/email.html', 'r') as file:
        contents = file.read()
    return Template(contents)

def SendEmail(subject, text, sender_email):
    if(os.environ['STAGE'] != 'dev'):
        lock.acquire()
        print('Sending email to', sender_email)
        footer_message = '\n\nReminder: This is a no-reply email, meaning that emails sent to this address will not be read.\nPlease send all concerns and inquiries at support@akadsph.com'

        header_subject = '[AKADS] ' + subject
        message = 'Subject: {}\n\n{}'.format(header_subject, text)
        message = MIMEMultipart()
        message['Subject'] = header_subject 
        message['From'] = gmail_user
        email_content = load_template()
        body = email_content.substitute(title=subject,text=text,buttonText='Visit Website',buttonLink='akadsph.com')

        message.attach(MIMEText(body, 'html'))
        # message.attach(MIMEText(text + footer_message, 'plain'))

        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(gmail_user, gmail_password)
        s.sendmail(gmail_user, sender_email, message.as_string())
        s.quit()
        lock.release()
