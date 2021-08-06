import boto3
import os

def PublishTextMessage(phonenumber, message):

    client = boto3.client(
        "sns",
        aws_access_key_id=os.environ['AWS_ID'],
        aws_secret_access_key=os.environ['AWS_KEY'],
        region_name=os.environ['AWS_REGION']
    )
    # Send your sms message.
    client.publish(
        PhoneNumber=phonenumber,
        Message='[AKADS] '+message
    )

    # client.publish(
    #     PhoneNumber='+639328461622',
    #     Message="Akads helps you match with a tutor that is most suited for your child. Create an account now and have your first hour for FREE."
    # )
