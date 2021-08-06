import requests
import json
import csv
import pandas as pd
import os

from dotenv import load_dotenv

load_dotenv()

base_url = os.environ['BASE_URL'] 
print(base_url)

s = requests.Session()
data = {
    'username': 'admin',
    'password': os.environ['ADMIN_PASS']
}

r = s.post(base_url+'/api-token-auth/',data)
print(r.text)

token = json.loads(r.text)['token']
headers = {
  'Authorization': 'JWT %s' % token
}

r = s.get(base_url+'/',headers=headers)

print('Check:',r)

subject_url = base_url+'/subject/'
shopitem_url = base_url+'/shop-item/'

with open('shopitems.json') as shopitems_json:
    with open('subjects.json') as subjects_json:
        shopitems = json.loads(''.join(shopitems_json.readlines()))
        subjects = json.loads(''.join(subjects_json.readlines()))
        for si in shopitems:
            payload = si
            r = s.post(shopitem_url,headers=headers,data=payload)
            print(r)
        for su in subjects:
            payload = su
            r = s.post(subject_url,headers=headers,data=payload)
            print(r)
