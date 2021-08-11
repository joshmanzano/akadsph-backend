from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Parent, Child, Subject, AdminParentConversation, AdminParentMessage
from core.serializers import SubjectSerializer
import os
import requests
import jwt
import json
import re
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('aug11.json') as f:
            data = json.loads(f.readline())

        df = pd.DataFrame(data)
        print('models')
        print(df['model'].unique())

        parent_rows = df[df['model'] == 'core.parent']
        parents = []
        for index, row in parent_rows.iterrows():
            parent = row['fields'] 
            parent['id'] = row['pk']

        tutor_rows = df[df['model'] == 'core.parent']
        parents = []
        for index, row in parent_rows.iterrows():
            parent = row['fields'] 
            parent['id'] = row['pk']



