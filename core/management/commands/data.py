from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Parent, Child, Tutor, TutorSubject, Subject, \
    AdminParentConversation, AdminParentMessage, AdminTutorConversation, AdminTutorMessage
from core.serializers import SubjectSerializer
import os
import requests
import jwt
import json
import re

blacklistEmail = []

with open('blacklist.json', 'r') as f:
    data = json.load(f)
    blacklistEmail = data['emails']

def cleanPhone(phonenum):
    try:
        if(phonenum.startswith('+63')):
            if(phonenum[3] == '0'):
                return '+63' + phonenum[4:]
            elif(phonenum[3] == '+'):
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



def createFolders(parent_fname, parent_lname, parent_id, subjects):

    ## Functions

    def createFolder(folder_name):
        url = os.environ['NEXTCLOUD_PARENTS']+folder_name

        payload={}
        headers = {
        'Authorization': os.environ['NEXTCLOUD_KEY'],
        'Cookie': 'cookie_test=test; __Host-nc_sameSiteCookielax=true; __Host-nc_sameSiteCookiestrict=true; oc_sessionPassphrase=%2Bcn4AjaZOjVC26NyMJM1pEXJBR07ZoXU2ReGBO3xdnosJ3fqdCNjwYKe6WRxSa3%2BsUwbnIpsZIJi7A0sk%2Bh8wykhq3EKIrh%2Be3lwUliRDMlJRruWz%2BMDI%2BO3lBrcIofm; ocvxou9w2hgj=512012323fe963d4c2546c226b27b4db'
        }

        requests.request("MKCOL", url, headers=headers, data=payload)

    folder_name = parent_fname+'-'+parent_lname+'-'+str(parent_id)

    ## Create Folders

    createFolder(folder_name)

    for s in subjects:
        createFolder(folder_name+'/'+s)

    ## Share Folder

    url = os.environ['NEXTCLOUD_SHARES']

    payload="{\n\"path\": \"/Parents/"+folder_name+"\",\n\"shareType\": 3,\n\"publicUpload\": \"true\"\n}"
    headers = {
    'OCS-APIRequest': 'true',
    'Authorization': os.environ['NEXTCLOUD_KEY'],
    'Content-Type': 'application/json',
    'Cookie': '__Host-nc_sameSiteCookielax=true; __Host-nc_sameSiteCookiestrict=true; oc_sessionPassphrase=%2Bcn4AjaZOjVC26NyMJM1pEXJBR07ZoXU2ReGBO3xdnosJ3fqdCNjwYKe6WRxSa3%2BsUwbnIpsZIJi7A0sk%2Bh8wykhq3EKIrh%2Be3lwUliRDMlJRruWz%2BMDI%2BO3lBrcIofm; ocvxou9w2hgj=512012323fe963d4c2546c226b27b4db'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data_dict = xmltodict.parse(response.text)

    return data_dict['ocs']['data']['url']

class Command(BaseCommand):

    def RegisterTutor(self, data):
            tutor = Tutor(username=data['username'].strip(),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            email=data['email'].strip().lower(),
            school=data['school'].strip(),
            course=data['course'].strip(),
            achievements=data['achievements'].strip(),
            phone=cleanPhone(data['phone']),
            picture=data['picture'],
            bank_name=data['bank_name'].strip(),
            bank_account_number=data['bank_account_number'],
            bank_account_name=data['bank_account_name'].strip(),
            bank_account_type=data['bank_account_type'].strip(),
            )
            tutor.save()
            return True

    def RegisterParent(self, data):
        parent = Parent(id=data['id'],
        username=data['username'].strip(),
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        email=data['email'].strip().lower(),
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

        if('child' in data):
            if(data['child']['age'] == ''):
                data['child']['age'] = None
            childData = data['child']
            child = Child(parent=parent,email=childData['email'].strip(),first_name=childData['first_name'].strip(),last_name=childData['last_name'].strip(),age=childData['age'],year_level=childData['year_level'].strip(),school=childData['school'].strip())
            child.save()

        return True
    
    def parentCheck(self, parent):
        email = parent['email']
        if(email in blacklistEmail):
            return False
        if(not re.match(r"[^@]+@[^@]+\.[^@]+",email)):
            return False
        return True

    def handle(self, *args, **options):
        with open('aug06.json') as f:
            data = json.loads(f.readline())

        parents = data['parents']
        children = {}
        errors = []

        for child in data['children']:
            children[child['parent']] = child


        for parent in parents:
            parent['last_name'] = parent['last_name'].capitalize()
            parent['first_name'] = parent['first_name'].strip()
            parent['email'] = parent['email'].strip().lower()
            parent['username'] = parent['email']
            parent['phone'] = cleanPhone(parent['phone'].strip())
            parent['first_time_user'] = True
            try:
                pass
                parent['child'] = children[parent['id']]
                # payload = json.dumps(parent)
                # r = s.post('%sregister-parent/' % api_url,headers=headers, data=payload)
                # print(r.status_code)
                # if(r.status_code != 200):
                #     with open('error.html', 'w') as errorfile:
                #         errorfile.write(r.text)
                #     print(r.status_code)
                #     errors.append(parent['email'])
            except:
                pass
                # print('No child',parent['first_name'],parent['last_name'])
            if(self.parentCheck(parent)):
                result = self.RegisterParent(parent)

        tutors = data['tutors']
        errors = []

        for tutor in tutors:
            tutor['last_name'] = tutor['last_name'].capitalize()
            tutor['first_name'] = tutor['first_name'].strip()
            tutor['email'] = tutor['email'].strip().lower()
            tutor['username'] = tutor['email']
            tutor['phone'] = '+63' + tutor['phone'].strip()
            tutor['first_time_user'] = True
            print(tutor['email'], tutor['first_name'])
            tutor['subjects'] = [] 
            try:
                for subject in tutor_subjects[tutor['email']]:
                    if (subject.strip() != '' and subject.strip() != 'Chinese'):
                        tutor['subjects'].append(subject)
            except:
                print(tutor['subjects'])
            tutor_id = tutor['id']
            payload = json.dumps(tutor)
            r = s.post('%sregister-tutor/' % api_url,headers=headers, data=payload)
            print(r.status_code)
            if(r.status_code != 200):
                with open('error.html', 'w') as errorfile:
                    errorfile.write(r.text)
                print(r.status_code)
                errors.append(tutor['email'])

        print(errors)