from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import GeneralPromo, UniquePromo, BrankasTransaction, SourcePayMongoTransaction, AdminTutorMessage, AdminTutorConversation, AdminParentMessage, AdminParentConversation, AccountLogger, Admin, ShopItem, TutorSubject, Parent, Tutor, Child, Requests, Feedback, Session, Conversation, Message, FavouriteTutor, PayMongoTransaction, AvailableDays, Subject, AdminSetting, ParentSetting, TutorSetting
from core.serializers import SubjectSerializer
import os
import requests
import jwt
import json
import re
import pandas as pd
from datetime import datetime
from tqdm import tqdm

def cleanData(data):
    for d in data:
        if(type(data[d]) == str):
            data[d] = data[d].strip()
        if d == 'email':
            data[d] = data[d].lower()
        if d == 'first_name' or d == 'last_name':
            data[d] = data[d].title()
        if d == 'phone':
            def checkPhone(phonenum):
                try:
                    if('.' in phonenum):
                        return ''
                    elif(phonenum.startswith('+63')):
                        if(phonenum == '+63'):
                            return ''
                        elif(phonenum[3] == '0'):
                            return '+63' + phonenum[4:]
                        elif(phonenum[3] == '+'):
                            if(phonenum[6:] == ''):
                                return ''
                            else:
                                return '+63' + phonenum[6:]
                        else:
                            return phonenum
                    else:
                        if(phonenum[0] == '0'):
                            return '+63' + phonenum[1:]
                        else:
                            return '+63' + phonenum
                except:
                    return ''
            data[d] = checkPhone(data[d].strip().replace(' ', ''))
            if(len(data[d]) != 13 and len(data[d]) != 11):
                data[d] = ''
    return data

def checkEmail(email, blacklistEmail):
    email = email.lower()
    if(email in blacklistEmail):
        return False
    if(not re.match(r"[^@]+@[^@]+\.[^@]+",email)):
        return False
    return True
    
def readParents(df, blacklistEmail):
    parent_rows = df[df['model'] == 'core.parent']
    parents = []
    parentID = []
    for index, row in parent_rows.iterrows():
        if(checkEmail(row['fields']['email'], blacklistEmail)):
            parent = cleanData(row['fields']) 
            parent['id'] = row['pk']
            parents.append(parent)
            parentID.append(parent['id'])
    return parents, parentID

def readChildren(df, parentID):
    child_rows = df[df['model'] == 'core.child']
    children = []
    for index, row in child_rows.iterrows():
        if(row['fields']['parent'] in parentID):
            child = cleanData(row['fields']) 
            child['id'] = row['pk']
            children.append(child)
    return children

def readTutors(df, blacklistEmail):
    tutor_rows = df[df['model'] == 'core.tutor']
    tutors = []
    for index, row in tutor_rows.iterrows():
        if(checkEmail(row['fields']['email'], blacklistEmail)):
            tutor = cleanData(row['fields']) 
            tutor['id'] = row['pk']
            tutors.append(tutor)
    return tutors

def RegisterTutor(data):
    tutor = Tutor(id=data['id'],
    username=data['username'],
    first_name=data['first_name'],
    last_name=data['last_name'],
    email=data['email'],
    school=data['school'],
    course=data['course'],
    achievements=data['achievements'],
    phone=data['phone'],
    picture=data['picture'],
    bank_name=data['bank_name'],
    bank_account_number=data['bank_account_number'],
    bank_account_name=data['bank_account_name'],
    bank_account_type=data['bank_account_type'],
    )
    tutor.save()

    return True

def RegisterParent(data):
    parent = Parent(id=data['id'],
    username=data['username'],
    first_name=data['first_name'],
    last_name=data['last_name'],
    email=data['email'],
    credits=data['credits'],
    status=data['status'],
    phone=data['phone'],
    picture=data['picture'],
    files=data['files'],
    referrer_code=data['referrer_code'],
    referrer_method=data['referrer_method'],
    survey=data['survey'],
    other_referrer=data['other_referrer'],
    fake_user=data['fake_user'],
    )
    parent.save()

    return True

def AddChild(data):
    child = Child(id=data['id'],
    parent=Parent.objects.get(id=data['parent']),
    email=data['email'],
    first_name=data['first_name'],
    last_name=data['last_name'],
    age=data['age'],
    year_level=data['year_level'],
    school=data['school'])
    child.save()

    return True

class Command(BaseCommand):
    help = 'Load data from json file to database.'

    def add_arguments(self, parser):
        parser.add_argument('dataPath', help='File path of json file to load')
        parser.add_argument('--blacklistPath', help='File path of email blacklist json file')

    def handle(self, *args, **options):
        blacklistEmail = []

        with open(options['blacklistPath'], 'r') as f:
            data = json.load(f)
            blacklistEmail = data['emails']

        with open(options['dataPath']) as f:
            data = json.loads(f.readline())

        df = pd.DataFrame(data)
        removeModel = ['auth.permission', 'auth.user', 'contenttypes.contenttype', 'sessions.session', \
            'core.paymongotransaction', 'core.sourcepaymongotransaction', 'core.brankastransaction', \
            'core.parentnotification', 'core.tutornotification', 'core.tutorpayout', 'core.shopitem', \
            'core.accountlogger', 'core.credittracker', 'core.admin']
        for model in removeModel:
            df = df.drop(df[df['model'] == model].index)

        print('Loading...')

        parents, parentID = readParents(df, blacklistEmail)
        df = df.drop(df[df['model'] == 'core.parent'].index)
        for parent in tqdm(parents):
            RegisterParent(parent)

        children = readChildren(df, parentID)
        df = df.drop(df[df['model'] == 'core.child'].index)
        for child in tqdm(children):
            AddChild(child)

        tutors = readTutors(df, blacklistEmail)
        df = df.drop(df[df['model'] == 'core.tutor'].index)
        for tutor in tqdm(tutors):
            RegisterTutor(tutor)

        rows = df[df['model'] == 'core.subject']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            obj = Subject(**data)
            obj.save()
        df = df.drop(rows.index)

        rows = df[df['model'] == 'core.requests']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['parent'] = Parent.objects.get(id=data['parent'])
                if(data['fav_tutor'] != None):
                    data['fav_tutor'] = Tutor.objects.get(id=data['fav_tutor'])
            except:
                continue
            data['child'] = Child.objects.get(id=data['child'])
            data['subject'] = Subject.objects.get(id=data['subject'])
            del data['declined_tutors']
            obj = Requests(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.availabledays']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['request'] = Requests.objects.get(id=data['request'])
            except:
                continue
            obj = AvailableDays(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.session']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            del data['start_zoom_link']
            del data['join_zoom_link']
            del data['zoom_id']
            del data['meet_link']
            try:
                data['request'] = Requests.objects.get(id=data['request'])
                data['tutor'] = Tutor.objects.get(id=data['tutor'])
            except:
                continue
            obj = Session(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.tutorsubject']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            data['subject'] = Subject.objects.get(id=data['subject'])
            try:
                data['tutor'] = Tutor.objects.get(id=data['tutor'])
            except:
                continue
            obj = TutorSubject(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.favourite_tutors']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['parent'] = Parent.objects.get(id=data['parent'])
                data['tutor'] = Tutor.objects.get(id=data['tutor'])
            except:
                continue
            obj = FavouriteTutor(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.adminparentconversation']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['parent'] = Parent.objects.get(id=data['parent'])
            except:
                continue
            obj = AdminParentConversation(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.admintutorconversation']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['tutor'] = Tutor.objects.get(id=data['tutor'])
            except:
                continue
            obj = AdminTutorConversation(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.conversation']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['parent'] = Parent.objects.get(id=data['parent'])
                data['tutor'] = Tutor.objects.get(id=data['tutor'])
                data['session'] = Session.objects.get(id=data['session'])
            except:
                continue
            obj = Conversation(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.adminparentmessage']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['ap_conversation'] = AdminParentConversation.objects.get(id=data['ap_conversation'])
            except:
                continue
            obj = AdminParentMessage(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.admintutormessage']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['at_conversation'] = AdminTutorConversation.objects.get(id=data['at_conversation'])
            except:
                continue
            obj = AdminTutorMessage(**data)
            obj.save()
        df = df.drop(rows.index)
        

        rows = df[df['model'] == 'core.message']
        for index, row in tqdm(rows.iterrows()):
            data = cleanData(row['fields']) 
            data['id'] = row['pk']
            try:
                data['conversation'] = Conversation.objects.get(id=data['conversation'])
            except:
                continue

                    
            obj = Message(**data)
            obj.save()
        df = df.drop(rows.index)
        

        Admin(
            username='akads.ph@gmail.com',
            email='akads.ph@gmail.com',
        ).save()

        shopItems = [
            {
            "amount": 4000.00,
            "name": "8 Hours",
            "credits": 8,
            "description": "8 Hour Bundle for 4000 PHP",
            "commission": 2400.00
            },
            {
            "amount": 5200.00,
            "name": "12 Hours",
            "credits": 12,
            "description": "12 Hour Bundle for 5200 PHP",
            "commission": 3600.00
            }
        ]
        

        for shopItem in shopItems:
            ShopItem(**shopItem).save()

        print('Successfully loaded!')

        # conversations = Conversation.objects.all()
        # with open('aug11chatlogs.txt','w') as f:
        #     for c in conversations:
        #         messages = Message.objects.filter(conversation=c)
        #         parent = c.parent
        #         tutor = c.tutor
        #         f.write(f'### {parent.first_name} - {tutor.first_name} ###\n')
        #         f.write('\n')
        #         for message in messages:
        #             if('Hello! My name is' not in message.text):
        #                 date = message.time_sent
        #                 if(data['sender'] == 'parent'):
        #                     line = f"{parent.first_name}: {message.text}"
        #                     f.write(date.strftime('%c')+'\n')
        #                     f.write(line+'\n')
        #                     f.write('\n')
        #                 elif(data['sender'] == 'tutor'):
        #                     line = f"{tutor.first_name}: {message.text}"
        #                     f.write(date.strftime('%c')+'\n')
        #                     f.write(line+'\n')
        #                     f.write('\n')
        #         f.write('#######\n')
        #         f.write('\n')

