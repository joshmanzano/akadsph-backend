from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from core.serializers import AdminTutorMessageSerializer, AdminTutorConversationSerializer, AdminParentMessageSerializer, AdminParentConversationSerializer, AccountLogger, ShopItemSerializer, TutorSubjectSerializer, UserSerializer, GroupSerializer, ParentSerializer, TutorSerializer, ChildSerializer, RequestsSerializer, FeedbackSerializer, SessionSerializer, ConversationSerializer, MessageSerializer, FavouriteTutorSerializer, PayMongoTransactionSerializer, AvailableDaysSerializer, SubjectSerializer, AdminSettingSerializer, ParentSettingSerializer, TutorSettingSerializer
from rest_framework.views import APIView
import requests
import json
import jwt
from rest_framework.response import Response
import smtplib
from rest_framework.generics import ListAPIView, ListCreateAPIView, DestroyAPIView, UpdateAPIView
from core.models import GeneralPromo, UniquePromo, BrankasTransaction, SourcePayMongoTransaction, AdminTutorMessage, AdminTutorConversation, AdminParentMessage, AdminParentConversation, AccountLogger, Admin, ShopItem, TutorSubject, Parent, Tutor, Child, Requests, Feedback, Session, Conversation, Message, FavouriteTutor, PayMongoTransaction, AvailableDays, Subject, AdminSetting, ParentSetting, TutorSetting
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import datetime
import xmltodict
import pytz
from core.extra_functions import getStartDateAndEndDateOfWeek
from core.ws import sendUpdate, sendBroadcast
import time
import random
import string
from django.conf import settings
import os
 

@api_view(['GET'])
def database_check(request):
    if request.method == 'GET':
        engine = settings.DATABASES['default']['ENGINE']
        host = settings.DATABASES['default']['HOST']
        return Response({
            'ENGINE': engine,
            'HOST': host
        })

# NextCloud API

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

def createTutorFolders(tutor_fname, tutor_lname, tutor_id):

    ## Functions

    def createFolder(folder_name):
        url = os.environ['NEXTCLOUD_TUTORS']+folder_name

        payload={}
        headers = {
        'Authorization': os.environ['NEXTCLOUD_KEY'],
        'Cookie': 'cookie_test=test; __Host-nc_sameSiteCookielax=true; __Host-nc_sameSiteCookiestrict=true; oc_sessionPassphrase=%2Bcn4AjaZOjVC26NyMJM1pEXJBR07ZoXU2ReGBO3xdnosJ3fqdCNjwYKe6WRxSa3%2BsUwbnIpsZIJi7A0sk%2Bh8wykhq3EKIrh%2Be3lwUliRDMlJRruWz%2BMDI%2BO3lBrcIofm; ocvxou9w2hgj=512012323fe963d4c2546c226b27b4db'
        }

        requests.request("MKCOL", url, headers=headers, data=payload)

    folder_name = tutor_fname+'-'+tutor_lname+'-'+str(tutor_id)

    ## Create Folders

    createFolder(folder_name)

    ## Share Folder

    url = os.environ['NEXTCLOUD_SHARES']

    payload="{\n\"path\": \"/Tutors/"+folder_name+"\",\n\"shareType\": 3,\n\"publicUpload\": \"true\"\n}"
    headers = {
    'OCS-APIRequest': 'true',
    'Authorization': os.environ['NEXTCLOUD_KEY'],
    'Content-Type': 'application/json',
    'Cookie': '__Host-nc_sameSiteCookielax=true; __Host-nc_sameSiteCookiestrict=true; oc_sessionPassphrase=%2Bcn4AjaZOjVC26NyMJM1pEXJBR07ZoXU2ReGBO3xdnosJ3fqdCNjwYKe6WRxSa3%2BsUwbnIpsZIJi7A0sk%2Bh8wykhq3EKIrh%2Be3lwUliRDMlJRruWz%2BMDI%2BO3lBrcIofm; ocvxou9w2hgj=512012323fe963d4c2546c226b27b4db'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data_dict = xmltodict.parse(response.text)

    return data_dict['ocs']['data']['url']



def decodeToken(token):
    data = jwt.decode(token, os.environ['SECRET_KEY'], algorithm='HS256')
    return data

# To get ID (primary key):
# pk = decodeToken(token)['id']

def promoCodes(parent_id, sitem, promo_code, amount):
    return_info = {}
    parent_ob = Parent.objects.get(id=parent_id)
    promo_type = promo_code[:4]
    # PROMO CODES LOGIC
    if promo_type == 'AKADS':
        try:
            gen_promo = GeneralPromo.objects.get(promoCode=promo_code, status=True)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo code not found"
            return Response(return_info)

        usedBy = gen_promo.usedBy.all()

        if parent_ob in usedBy:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: You have already used this code"
            return Response(return_info)

        timezone.activate(pytz.timezone("Asia/Manila"))
        if gen_promo.promoPeriod < timezone.localtime(timezone.now()):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo code is not available anymore"
            gen_promo.status = False
            gen_promo.save()
            return Response(return_info)

        if sitem != gen_promo.type:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo Code used does not match shop item"
            return Response(return_info)

        amount = amount - (amount * gen_promo.discount)
        gen_promo.usedBy.add(parent_ob)
        if usedBy.count() == gen_promo.maxUsage:
            gen_promo.status = False

        gen_promo.save()

        # It's free, no need to make a paymongo request
        # if amount == 0:
        #     sitem.timesBought = sitem.timesBought + 1
        #     sitem.save()
        #     parent_ob.credits = parent_ob.credits + sitem.credits
        #     parent_ob.save()
        #     return Response(parent_ob)

    else:
        try:
            print(promo_code)
            print(parent_id)
            uni_promo = UniquePromo.objects.get(promoCode=promo_code, linkedAccount=parent_id, status=True)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo code not found"
            return return_info

        timezone.activate(pytz.timezone("Asia/Manila"))
        if uni_promo.terminationPeriod < timezone.localtime(timezone.now()):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo code is not available anymore"
            uni_promo.status = False
            uni_promo.save()
            return return_info

        if sitem != uni_promo.type:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Promo Code used does not match shop item"
            return return_info

        amount = amount - uni_promo.discount
        uni_promo.status = False
        uni_promo.save()

        # It's free, no need to make a paymongo request
        # if amount == 0:
        #     sitem.timesBought = sitem.timesBought + 1
        #     sitem.save()
        #     parent_ob.credits = parent_ob.credits + sitem.credits
        #     parent_ob.save()
        #     return Response(parent_ob)
        print('success in promo')
        return_info['return_status'] = 'success'
        return_info['amount'] = amount
        print(return_info)
        return return_info

# TO DEPRECIATE
class AddCredits(APIView):
    """
    POST:
    Description: Add credits
    Input:
    {
        "parent_id": id of parent,
        "credits": int
    }
    Output:
    {
        "parent": parent object
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        credits = request.data['credits']

        parent = Parent.objects.get(id=parent_id)
        parent.credits += credits
        parent.save()

        return Response(ParentSerializer(parent).data)

# TO DEPRECIATE - POSSIBLY FOR ADMIN
class ApproveTutor(APIView):
    """
    POST:
    Description: Changes a tutor's status from False to true
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "username": string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "school": string,
        "course": string,
        "achievements": string,
        "rating": float,
        "subjects": string,
        "zoominfo": string,
        "status": boolean
    }
    """
    def post(self, request, format=None):
        request_id = request.data['tutor_id']
        tutor_ob = Tutor.objects.get(pk=request_id)

        tutor_ob.status = True
        tutor_ob.save()

        tutor_serializer = TutorSerializer(tutor_ob)
        return Response(tutor_serializer.data)

# TO DEPRECIATE
class SpecificParentUsername(APIView):
    """
    POST:
    Description: Find specific parent by username
    Input:
    {
    "username": string
    }
    """
    def post(self, request, format=None):
        username = request.data['username']

        queryset = Parent.objects.get(username=username)
        serializer_class = ParentSerializer(queryset)

        return Response(serializer_class.data)

# TO DEPRECIATE - POSSIBLY FOR ADMIN
class FindPendingRequests(APIView):
    """
    GET:
    Description: Get all pending requests
    Input: N/A
    """
    def get(self, request, format=None):
        queryset = Requests.objects.filter(status='pending')
        serializer_class = RequestsSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class FindAcceptedRequestsAndSessionsParentDate(APIView):
    """
    POST:
    Description: Get all accepted requests based on parent id and current date
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        request object
    }
    """

    def post(self, request, format=None):
        parent_id = request.data['parent_id']

        queryset = Requests.objects.filter(parent=parent_id).filter(status='accepted')
        serializer_class = RequestsSerializer(queryset, many=True)

        requestsSet = []

        for r in serializer_class.data:
            if r['start_date_time'].split("T")[0] == str(timezone.now().date()):
                requestsSet.append(r)

        return Response(requestsSet)

# TO DEPRECIATE
class FindAcceptedRequestsAndSessionsTutorDate(APIView):
    """
    POST:
    Description: Get all accepted requests based on tutor id and current date
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string
    }
    """

    def post(self, request, format=None):
        tutor_id = request.data['tutor_id']

        tutor = Tutor.objects.get(id=tutor_id)

        queryset = Requests.objects.filter(tutor_email=tutor.email).filter(status='accepted')
        serializer_class = RequestsSerializer(queryset, many=True)

        requestsSet = []

        for r in serializer_class.data:
            if r['start_date_time'].split("T")[0] == str(timezone.now().date()):
                requestsSet.append(r)

        return Response(requestsSet)

# TO DEPRECIATE
class FindFinishedRequestsUser(APIView):
    """
    POST:
    Description: Get all finished requests based on parent id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string
    }
    """

    def post(self, request, format=None):
        parent_id = request.data['parent_id']

        queryset = Requests.objects.filter(parent=parent_id).filter(status='finished')
        serializer_class = RequestsSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class FindPendingRequestsUser(APIView):
    """
    POST:
    Description: Get all pending requests based on parent id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string
    }
    """

    def post(self, request, format=None):
        parent_id = request.data['parent_id']

        queryset = Requests.objects.filter(parent=parent_id).filter(status='pending')
        serializer_class = RequestsSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class AllParentsFinishedSessions(APIView):
    """
    POST:
    Description: Get All finished sessions of a certain parent via parent id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        queryset = Requests.objects.filter(parent=parent_id).filter(status='finished')
        serializer_class = RequestsSerializer(queryset, many=True)

        FinishedRequestsSet = []

        for r in serializer_class.data:
            FinishedRequestsSet.append(r)
            session = Session.objects.get(request=r['id'])
            r['zoom_link'] = session.zoom_link

        return Response(FinishedRequestsSet)

# TO DEPRECIATE
class AllTutorsFinishedSessions(APIView):
    """
    POST:
    Description: Get All finished sessions of a certain tutor via tutor email
    Input:
    {
        "tutor_email": string
    }
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string
    }
    """
    def post(self, request, format=None):
        tutor_email = request.data['tutor_email']
        queryset = Requests.objects.filter(tutor_email=tutor_email).filter(status='finished')
        serializer_class = RequestsSerializer(queryset, many=True)

        FinishedRequestsSet = []

        for r in serializer_class.data:
            FinishedRequestsSet.append(r)
            session = Session.objects.get(request=r['id'])
            r['zoom_link'] = session.zoom_link

        return Response(FinishedRequestsSet)

# TO DEPRECIATE - POSSIBLY FOR ADMIN
class PendingTutors(APIView):
    def get(self, request, format=None):
        queryset = Tutor.objects.filter(status=False)
        serializer_class = TutorSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class ParentRequests(APIView):
    def get(self, request, pk, format=None):
        queryset = Requests.objects.filter(parent=pk)
        serializer_class = RequestsSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class TutorRequests(APIView):
    """
    GET:
    Description: Get all sessions of a certain tutor (based on email)
    Output:
    {
    "parent": id of parent,
    "child": id of child,
    "tutor_email": string,
    "start_date_time": Datetime,
    "end_date_time": Datetime,
    "time": Datetime,
    "extra_files": string,
    "status": string
    }
    """
    def get(self, request, email, format=None):
        queryset = Requests.objects.filter(tutor_email=email)
        serializer_class = RequestsSerializer(queryset, many=True)

        return Response(serializer_class.data)

# TO DEPRECIATE
class UpdateParent(APIView):
    """
    PUT:
    Description: Updates a parent based on the Primary Key given
    Output:
    {
        "username": string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "credits": float,
        "status": boolean
    }
    """
    def put(self, request, pk, format=None):
        queryset = Parent.objects.get(id=pk)
        serializer_class = ParentSerializer(queryset, data=request.data)

        if serializer_class.is_valid():
            serializer_class.save()
            return Response(serializer_class.data)

        return Response(status=status.HTTP_204_BAD_REQUEST)

# TO DEPRECIATE
class UpdateTutor(APIView):
    """
    PUT:
    Description: Updates a tutor based on the Primary Key given
    Output:
    {
        "username": string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "school": string,
        "course": string,
        "achievements": string,
        "rating": float,
        "subjects": string,
        "zoominfo": string,
        "status": boolean
    }
    """
    def put(self, request, pk, format=None):
        queryset = Tutor.objects.get(id=pk)
        serializer_class = TutorSerializer(queryset, data=request.data)

        if serializer_class.is_valid():
            serializer_class.save()
            return Response(serializer_class.data)

        return Response(status=status.HTTP_204_BAD_REQUEST)

# TO DEPRECIATE
class DeleteFeedbackView(APIView):
    """
    DELETE:
    Description: Deletes Feedback object based on Primary key given
    Output: None
    """
    def delete(self, request, pk, format=None):
        feedback = Feedback.objects.get(id=pk).delete()
        return Response(None)

# TO DEPRECIATE
class DeleteChildView(APIView):
    """
    DELETE:
    Description: Deletes child object based on Primary key given
    Output: None
    """
    def delete(self, request, pk, format=None):
        child = Child.objects.filter(id=pk).delete()
        return Response(None)

# TO DEPRECIATE
class DeleteParentView(APIView):
    """
    DELETE:
    Description: Deletes Parent object based on Primary key given
    Output: None
    """
    def delete(self, request, pk, format=None):
        parent = Parent.objects.get(id=pk).delete()
        return Response(None)

# TO DEPRECIATE
class DeleteTutorView(APIView):
    """
    DELETE:
    Description: Deletes tutor object based on Primary key given
    Output: None
    """
    def delete(self, request, pk, format=None):
        tutor = Tutor.objects.filter(id=pk).delete()
        return Response(None)

# TO DEPRECIATE
class PurgeUserView(APIView):
    """
    DELETE:
    Description: Clears both parents and tutors 
    Output: None
    """
    def delete(self, request, format=None):
        Parent.objects.all().delete()
        Tutor.objects.all().delete()
        TutorSubject.objects.all().delete()
        Child.objects.all().delete()
        return Response(None)

#### Authentication API

class LoginParent(APIView):
    def post(self, request, format=None):
        googleUrl = 'https://oauth2.googleapis.com/tokeninfo'
        response = requests.get(googleUrl, params={'id_token': request.data['id_token']})
        data = json.loads(response.text)
        try:
            googleEmail = data['email']
            try:
                admin = Admin.objects.get(email=googleEmail)
                payload = {
                    'id':admin.id,
                    'sub':admin.username,
                    'type':'admin'
                }
                encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                data['exists'] = True
                data['session_token'] = encoded_jwt
                return Response(data)
            except ObjectDoesNotExist:
                pass
            try:
                parent = Parent.objects.get(email=googleEmail)
                payload = {
                    'id':parent.id,
                    'sub':parent.username,
                    'type':'parent'
                }
                encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                data['exists'] = True
                data['session_token'] = encoded_jwt
                try:
                    parent.picture = data['picture']
                    parent.save()
                except Exception as e:
                    print(e)

                timezone.activate(pytz.timezone("Asia/Manila"))
                AccountLogger(time=timezone.localtime(timezone.now()), type='Parent', google_data=str(data)).save()
                sendBroadcast('%s (Parent) logged in!' % googleEmail)
                return Response(data)
            except ObjectDoesNotExist:
                data['exists'] = False
                return Response(data)
        except Exception as e:
            data['exists'] = False
            data['error'] = str(e)
            return Response(data)

class LoginTutor(APIView):
    def post(self, request, format=None):
        googleUrl = 'https://oauth2.googleapis.com/tokeninfo'
        response = requests.get(googleUrl, params={'id_token': request.data['id_token']})
        data = json.loads(response.text)
        try:
            googleEmail = data['email']
            try:
                admin = Admin.objects.get(email=googleEmail)
                payload = {
                    'id':admin.id,
                    'sub':admin.username,
                    'type':'admin'
                }
                encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                data['exists'] = True
                data['session_token'] = encoded_jwt
                return Response(data)
            except ObjectDoesNotExist:
                pass
            try:
                tutor = Tutor.objects.get(email=googleEmail)
                payload = {
                    'id':tutor.id,
                    'sub':tutor.username,
                    'type':'tutor'
                }
                encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                data['exists'] = True
                data['session_token'] = encoded_jwt
                tutor.picture = data['picture']
                tutor.save()
                timezone.activate(pytz.timezone("Asia/Manila"))
                AccountLogger(time=timezone.localtime(timezone.now()), type='Tutor', google_data=str(data)).save()
                sendBroadcast('%s (Tutor) logged in!' % googleEmail)
                return Response(data)
            except ObjectDoesNotExist:
                data['exists'] = False
                return Response(data)
        except Exception as e:
            return Response(data)

        tutor = Tutor(username=data['sub'],
        first_name=data['given_name'],
        last_name=data['family_name'],
        email=data['email'],
        phone='',
        picture=data['picture'])
        tutor.save()
        payload = {
            'id':tutor.id,
            'sub':tutor.username,
            'type':'tutor'
        }
        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
        data['exists'] = True
        data['session_token'] = encoded_jwt
        return Response(data)

class ReceiveTutorEmail(APIView):
    def post(self, request, format=None):
        googleEmail = request.data['email']
        print(googleEmail)
        sendBroadcast('[TUTOR EMAIL] %s' % googleEmail)
        return Response(request.data)

class RegisterAdmin(APIView):
    def post(self, request, format=None):
        admin= Admin(username=request.data['username'],
        email=request.data['email'])
        admin.save()

        payload = {
            'id':admin.id,
            'sub':admin.username,
            'type':'admin'
        }

        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
        return Response(encoded_jwt)

class RegisterParent(APIView):
    def post(self, request, format=None):
        print(request.data)
        parent = Parent(username=request.data['username'].strip(),
        first_name=request.data['first_name'].strip(),
        last_name=request.data['last_name'].strip(),
        email=request.data['email'].strip().lower(),
        phone='+63'+request.data['phone'],
        picture=request.data['picture'],
        referrer_code=request.data['referral_code'],
        referrer_method=request.data['referrer'],
        other_referrer=request.data['other'],
        survey=request.data['survey'],
        credits=1)
        parent.save()
        # childData = request.data['child']
        # if(childData['age'] == ''):
        #     childData['age'] = None
        # child = Child(parent=parent,email=childData['email'],first_name=childData['first_name'],last_name=childData['last_name'],age=childData['age'],year_level=childData['year_level'],school=childData['school'])
        # child.save()
        payload = {
            'id':parent.id,
            'sub':parent.username,
            'type':'parent'
        }

        if(os.environ['STAGE'] == 'dev'):
            pass
        else:
            #get all subjects
            queryset = Subject.objects.all()
            serializer_class = SubjectSerializer(queryset, many=True)

            subjects = []

            print(serializer_class.data)
            for subject in serializer_class.data:
                print(subject)
                subjects.append(subject['subject_field'])

            try:
                parent.files = createFolders(parent.first_name, parent.last_name, parent.id, subjects)
                parent.save()
            except:
                pass

        #create conversation with admin and send a default message
        conversation = AdminParentConversation(parent=parent)
        conversation.save()

        message = AdminParentMessage(ap_conversation=conversation,
            sender='admin',
            text='Hello, ' + parent.first_name + '! If you have any inquiries or concerns, please feel free to message me!')
        message.save()

        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
        return Response(encoded_jwt)

class RegisterTutor(APIView):
    def post(self, request, format=None):
        tutor = Tutor(username=request.data['username'].strip(),
        first_name=request.data['first_name'].strip(),
        last_name=request.data['last_name'].strip(),
        email=request.data['email'].strip().lower(),
        school=request.data['school'].strip(),
        course=request.data['course'].strip(),
        achievements=request.data['achievements'].strip(),
        phone='+63'+request.data['phone'],
        picture=request.data['picture'],
        bank_name=request.data['bank_name'].strip(),
        bank_account_number=request.data['bank_account_number'],
        bank_account_name=request.data['bank_account_name'].strip(),
        bank_account_type=request.data['bank_account_type'].strip(),
        )

        tutor.save()

        for subject_field in request.data['subjects']:
            subject = Subject.objects.get(subject_field=subject_field)
            tutorSubject = TutorSubject(tutor=tutor, subject=subject)
            tutorSubject.save()

        try:
            tutor.files = createTutorFolders(tutor.first_name, tutor.last_name, tutor.id)
            tutor.save()
        except:
            pass

        payload = {
            'id':tutor.id,
            'sub':tutor.username,
            'type':'tutor'
        }

        conversation = AdminTutorConversation(tutor=tutor)
        conversation.save()

        message = AdminTutorMessage(at_conversation=conversation,
            sender='admin',
            text='Hello, ' + tutor.first_name + '! If you have any inquiries or concerns, please feel free to message me!')
        message.save()

        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
        return Response(encoded_jwt)

class TokenInfo(APIView):
    def post(self, request, format=None):
        try:
            data = jwt.decode(request.data['session_token'], os.environ['SECRET_KEY'], algorithm='HS256')
            if(data['type'] == 'parent'):
                parent = Parent.objects.get(id=data['id'])
            if(data['type'] == 'tutor'):
                tutor = Tutor.objects.get(id=data['id'])
            data['verified'] = True
            return Response(data)
        except:
            data = {
                'verified': False
            }
            return Response(data)

class LoginAs(APIView):
    def post(self, request, format=None):
        try:
            data = jwt.decode(request.data['session_token'], os.environ['SECRET_KEY'], algorithm='HS256')
            user = request.data['user']
            if(data['type'] == 'admin'):
                if(user['type'] == 'parent'):
                    try:
                        parent = Parent.objects.get(email=user['email'])
                        data = {}
                        payload = {
                            'id':parent.id,
                            'sub':parent.username,
                            'type':'parent'
                        }
                        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                        data['exists'] = True
                        data['session_token'] = encoded_jwt
                        return Response(data)
                    except ObjectDoesNotExist:
                        data['exists'] = False
                        return Response(data)                   
                elif(user['type'] == 'tutor'):
                    try:
                        tutor = Tutor.objects.get(email=user['email'])
                        data = {}
                        payload = {
                            'id':tutor.id,
                            'sub':tutor.username,
                            'type':'tutor'
                        }
                        encoded_jwt = jwt.encode(payload, os.environ['SECRET_KEY'], algorithm='HS256')
                        data['exists'] = True
                        data['session_token'] = encoded_jwt
                        return Response(data)
                    except ObjectDoesNotExist:
                        data['exists'] = False
                        return Response(data)
            data['verified'] = False
            return Response(data)
        except Exception as e:
            data = {
                'verified': False,
                'error': e
            }
            return Response(data)


### External API

class ZoomAPI(APIView):
    """
    tutee, subject, start_time, duration
    """
    def post(self, request, format=None):
        url = "https://api.zoom.us/v2/users/me/meetings"
        currentTime = int(datetime.datetime.now().timestamp())
        token_data = {
            "aud": None,
            "iss": "P9xBzrKFSTmhu_Ca0EfP0w",
            "exp": currentTime + 3600,
            "iat": currentTime
        }
        access_token = jwt.encode(token_data, zoom_api_secret, algorithm='HS256').decode('utf8')
        tutee = request.data['tutee']
        subject = request.data['subject']
        start_time = request.data['start_time']
        duration = str(request.data['duration'])
        timezone = 'Asia/Singapore'

        # Examples
        # start_time = "2020-12-27T21:30:00"
        # duration = "60"
        # timezone = "Asia/Singapore"

        payload = "{\n    \"topic\": \"AKADS - %s - %s\",\n    \"type\": 2,\n    \"start_time\": \"%s\",\n    \"duration\": %s,\n    \"timezone\": \"%s\",\n    \"settings\": {\n        \"waiting_room\": false,\n        \"auto_recording\": \"local\"\n    }\n}" % (tutee, subject, start_time, duration, timezone)
        headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/json',
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        data = json.loads(response.text.encode('utf8'))

        response = {
            'start': data['start_url'],
            'join': data['join_url']
        }

        return Response(response)

class TwilioAPI(APIView):
    """
    phone_num
    """
    def post(self, request, format=None):
        # Download the helper library from https://www.twilio.com/docs/python/install

        # Your Account Sid and Auth Token from twilio.com/console
        # DANGER! This is insecure. See http://twil.io/secure
        account_sid = 'AC01b0bdcd18fe80820225189cbdb6419b'
        auth_token = '70da150c32a9d7e251ccd0ed39db103f'
        client = Client(account_sid, auth_token)

        message = client.messages \
                        .create(
                            body="AKADS allows parents to book college student tutors for their Grade 1-10 children. We tutor Math, Science, English and Filipino.",
                            from_='+16592224235',
                            to=request.data['phone_num']
                        )

        data = {
            'to':request.data['phone_num']
        }

        return Response(data)

class EmailAPI(APIView):
    """
    recipient, message
    """
    def post(self, request, format=None):
        gmail_user = 'akads.ph@gmail.com'
        gmail_password = '1akadsph!'

        recipient = request.data['recipient']
        message = request.data['message']

        # # creates SMTP session
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        # # Authentication
        s.login(gmail_user, gmail_password)

        # # sending the mail
        s.sendmail(gmail_user, recipient, message)

        # # terminating the session
        s.quit()

        data = {
            'recipient': recipient,
            'message': message
        }

        return Response(data)

class SourcePayMongoAPI(APIView):
    """
    POST:
    Description:
    Input:
    {
        "parent_id": id of parent making transaction,
        "promo_code": string,
        "shop_item": id of shop item
    }
    """
    def post(self, request, format=None):
        return_info = {}

        # amount = int(request.data['amount']) * 100
        parent_id = request.data['parent_id']
        promo_code = request.data['promo_code']
        promo_type = ""
        shop_item = request.data['shop_item']
        success_url = request.data['success_url']
        failed_url = request.data['failed_url']
        source_type = request.data['source_type']

        parent_ob = Parent.objects.get(id=parent_id)

        try:
            sitem = ShopItem.objects.get(id=shop_item, archived=False)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Shop Item not found"
            return Response(return_info)

        credits = sitem.credits
        promo_code_info = promoCodes(parent_id, sitem, promo_code, sitem.amount)
        print(promo_code_info)
        if(promo_code_info['return_status'] == 'success'):
            print(promo_code_info['amount'])
            amount = int(promo_code_info['amount']) * 100
        else:
            amount = sitem.amount * 100

        # sendBroadcast('%s %s is buying %s credit/s!' % (parent_ob.first_name, parent_ob.last_name, str(credits)) )

        url = "https://api.paymongo.com/v1/sources"

        payload = {"data": {"attributes": {
                    "amount": amount,
                    "redirect": {
                        "success": success_url,
                        "failed": failed_url
                    },
                    "type": source_type,
                    "billing": {
                        "name": parent_ob.first_name + ' ' + parent_ob.last_name,
                        "phone": parent_ob.phone,
                        "email": parent_ob.email
                    },
                    "currency": "PHP"
                }}}
    
        print(payload)

        headers = paymongo_headers

        response = requests.request("POST", url, json=payload, headers=headers)

        print(response.text)
        res = json.loads(response.text)['data']

        src_id = res['id']
        checkout_url = res['attributes']['redirect']['checkout_url']

        parent = Parent.objects.get(id=parent_id)
        parent.first_buy = True
        parent.save()

        # credits = 0
        #
        # if(amount == 54900):
        #     credits = 1
        # elif(amount == 499900):
        #     credits = 10
        # elif(amount == 719900):
        #     credits = 20

        # Modify amount here --> FOR NOW

        timezone.activate(pytz.timezone("Asia/Manila"))
        transaction = SourcePayMongoTransaction(parent=parent, src_id=src_id, credits=credits, amount=amount, date=timezone.localtime(timezone.now()))
        transaction.save()

        # Shop Item stats
        sitem.timesBought = sitem.timesBought + 1
        sitem.save()
        print('success')
        print(src_id)
        print(checkout_url)

        return Response({
            'src_id': src_id,
            'checkout_url': checkout_url
        })

class VerifySourcePayMongoAPI(APIView):
    def post(self, request, format=None):
        src_id = request.data['src_id']
        parent_id = request.data['parent_id']

        try:
            parent = Parent.objects.get(id=parent_id)
            transaction = SourcePayMongoTransaction.objects.get(parent=parent, src_id=src_id)

            url = 'https://api.paymongo.com/v1/sources/'+src_id

            payload={}
            # headers = {
            # 'Authorization': 'Basic cGtfdGVzdF9MaUJpWXRoeDFEMzZoUVlWY1BTUkIyTUo6'
            # }
            headers = paymongo_headers
            response = requests.request("GET", url, headers=headers, data=payload)
            res = json.loads(response.text)

            if(res['data']['attributes']['status'] == 'chargeable'):
                url = "https://api.paymongo.com/v1/payments"

                payload = {"data": {"attributes": {
                            "amount": int(transaction.amount),
                            "source": {
                                "id": src_id,
                                "type": "source"
                            },
                            "currency": "PHP",
                            "description": parent.email 
                        }}}
                headers = paymongo_headers

                response = requests.request("POST", url, json=payload, headers=headers)
                print(response)
                print(response.text)

                pay_data = json.loads(response.text)['data']
                if(pay_data['attributes']['status'] == 'paid' and not transaction.status):
                    transaction.pay_id = pay_data['id']
                    transaction.status = True
                    transaction.save()
                    parent.credits += transaction.credits
                    parent.save()
                    return Response(True)

            return Response(False)
        except:
            return Response(False)

        return Response(False)

class BrankasAPI(APIView):
    """
    POST:
    Description:
    Input:
    {
        "parent_id": id of parent making transaction,
        "promo_code": string,
        "shop_item": id of shop item
    }
    """
    def post(self, request, format=None):
        return_info = {}

        # amount = int(request.data['amount']) * 100
        parent_id = request.data['parent_id']
        promo_code = request.data['promo_code']
        promo_type = ""
        shop_item = request.data['shop_item']
        success_url = request.data['success_url']
        failed_url = request.data['failed_url']
        ref_id = str(int(time.time())).join(random.choice(string.digits) for i in range(3))  

        if promo_code != "":
            promo_type = promo_code[0:3]

        parent_ob = Parent.objects.get(id=parent_id)

        try:
            sitem = ShopItem.objects.get(id=shop_item, archived=False)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Shop Item not found"
            return Response(return_info)

        credits = sitem.credits
        amount = sitem.amount * 100
        sendBroadcast('%s %s is buying %s credit/s!' % (parent_ob.first_name, parent_ob.last_name, str(credits)) )

        # PROMO CODES LOGIC
        if promo_type == 'GEN':
            try:
                gen_promo = GeneralPromo.objects.get(promoCode=promo_code, status=True)
            except:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code not found"
                return Response(return_info)

            usedBy = gen_promo.usedBy.all()

            if parent_ob in usedBy:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: You have already used this code"
                return Response(return_info)

            timezone.activate(pytz.timezone("Asia/Manila"))
            if gen_promo.promoPeriod < timezone.localtime(timezone.now()):
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code is not available anymore"
                gen_promo.status = False
                gen_promo.save()
                return Response(return_info)

            if sitem != gen_promo.type:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo Code used does not match shop item"
                return Response(return_info)

            amount = amount - (amount * gen_promo.discount)
            gen_promo.usedBy.add(parent_ob)
            if usedBy.count() == gen_promo.maxUsage:
                gen_promo.status = False

            gen_promo.save()

            # It's free, no need to make a paymongo request
            if amount == 0:
                sitem.timesBought = sitem.timesBought + 1
                sitem.save()
                parent_ob.credits = parent_ob.credits + sitem.credits
                parent_ob.save()
                return Response(parent_ob)

        elif promo_type == 'UNI':
            try:
                uni_promo = UniquePromo.objects.get(promoCode=promo_code, linkedAccount=parent_id, status=True)
            except:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code not found"
                return Response(return_info)

            timezone.activate(pytz.timezone("Asia/Manila"))
            if uni_promo.terminationPeriod < timezone.localtime(timezone.now()):
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code is not available anymore"
                uni_promo.status = False
                uni_promo.save()
                return Response(return_info)

            if sitem != uni_promo.type:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo Code used does not match shop item"
                return Response(return_info)

            amount = amount - (amount * uni_promo.discount)
            uni_promo.status = False
            uni_promo.save()

            # It's free, no need to make a paymongo request
            if amount == 0:
                sitem.timesBought = sitem.timesBought + 1
                sitem.save()
                parent_ob.credits = parent_ob.credits + sitem.credits
                parent_ob.save()
                return Response(parent_ob)

        url = brankas_url + "/v1/checkout"

        payload = json.dumps({
        "from": {
            "type": "BANK",
            "country": "PH"
        },
        "destination_account_id": brankas_dest,
        "amount": {
            "cur": "PHP",
            "num": str(amount)
        },
        "memo": str(sitem.name),
        "customer": {
            "fname": parent_ob.first_name,
            "lname": parent_ob.last_name,
            "email": parent_ob.email,
            "mobile": parent_ob.phone,
        },
        "reference_id": ref_id,
        "payment_channel": "_",
        "client": {
            "display_name": "Akads",
            "logo_url": "https://www.akadsph.com/static/whitelogo.png",
            "return_url": success_url,
            "fail_url": failed_url,
            "deep_link": True
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': brankas_api 
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        res = json.loads(response.text)
        print(res)

        transfer_id = res['transaction_id']
        checkout_url = res['redirect_uri']

        parent = Parent.objects.get(id=parent_id)
        parent.first_buy = True
        parent.save()

        # credits = 0
        #
        # if(amount == 54900):
        #     credits = 1
        # elif(amount == 499900):
        #     credits = 10
        # elif(amount == 719900):
        #     credits = 20

        # Modify amount here --> FOR NOW

        timezone.activate(pytz.timezone("Asia/Manila"))
        transaction = BrankasTransaction(parent=parent, transfer_id=transfer_id, ref_id=ref_id, credits=credits, amount=amount, date=timezone.localtime(timezone.now()))
        transaction.save()

        # Shop Item stats
        sitem.timesBought = sitem.timesBought + 1
        sitem.save()

        return Response({
            'transfer_id': transfer_id,
            'checkout_url': checkout_url
        })

class VerifyBrankasAPI(APIView):
    def post(self, request, format=None):
        transfer_id = request.data['transfer_id']
        parent_id = request.data['parent_id']

        try:
            parent = Parent.objects.get(id=parent_id)
            transaction = BrankasTransaction.objects.get(parent=parent, transfer_id=transfer_id)

            print(transaction)

            url = '%s/v1/transfer?transfer_ids=%s' % (brankas_url,transfer_id)

            payload={}
            headers = {
            'Content-Type': 'application/json',
            'x-api-key': brankas_api 
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            res = json.loads(response.text)

            if(res['transfers'][0]['status'] == 'SUCCESS' and not transaction.status):
                parent.credits += transaction.credits
                transaction.status = True
                parent.save()
                transaction.save()
                return Response(True)

            return Response(False)
        except:
            return Response(False)

        return Response(False)


class PayMongoAPI(APIView):
    """
    POST:
    Description:
    Input:
    {
        "parent_id": id of parent making transaction,
        "promo_code": string,
        "shop_item": id of shop item
    }
    """
    def post(self, request, format=None):
        return_info = {}

        # amount = int(request.data['amount']) * 100
        parent_id = request.data['parent_id']
        promo_code = request.data['promo_code']
        promo_type = ""
        shop_item = request.data['shop_item']


        if promo_code != "":
            promo_type = promo_code[0:3]

        parent_ob = Parent.objects.get(id=parent_id)

        try:
            sitem = ShopItem.objects.get(id=shop_item, archived=False)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Shop Item not found"
            return Response(return_info)

        credits = sitem.credits
        amount = sitem.amount * 100
        sendBroadcast('%s %s is buying %s credit/s!' % (parent_ob.first_name, parent_ob.last_name, str(credits)) )

        # PROMO CODES LOGIC
        if promo_type == 'GEN':
            try:
                gen_promo = GeneralPromo.objects.get(promoCode=promo_code, status=True)
            except:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code not found"
                return Response(return_info)

            usedBy = gen_promo.usedBy.all()

            if parent_ob in usedBy:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: You have already used this code"
                return Response(return_info)

            timezone.activate(pytz.timezone("Asia/Manila"))
            if gen_promo.promoPeriod < timezone.localtime(timezone.now()):
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code is not available anymore"
                gen_promo.status = False
                gen_promo.save()
                return Response(return_info)

            if sitem != gen_promo.type:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo Code used does not match shop item"
                return Response(return_info)

            amount = amount - (amount * gen_promo.discount)
            gen_promo.usedBy.add(parent_ob)
            if usedBy.count() == gen_promo.maxUsage:
                gen_promo.status = False

            gen_promo.save()

            # It's free, no need to make a paymongo request
            if amount == 0:
                sitem.timesBought = sitem.timesBought + 1
                sitem.save()
                parent_ob.credits = parent_ob.credits + sitem.credits
                parent_ob.save()
                return Response(parent_ob)

        elif promo_type == 'UNI':
            try:
                uni_promo = UniquePromo.objects.get(promoCode=promo_code, linkedAccount=parent_id, status=True)
            except:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code not found"
                return Response(return_info)

            timezone.activate(pytz.timezone("Asia/Manila"))
            if uni_promo.terminationPeriod < timezone.localtime(timezone.now()):
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo code is not available anymore"
                uni_promo.status = False
                uni_promo.save()
                return Response(return_info)

            if sitem != uni_promo.type:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Promo Code used does not match shop item"
                return Response(return_info)

            amount = amount - (amount * uni_promo.discount)
            uni_promo.status = False
            uni_promo.save()

            # It's free, no need to make a paymongo request
            if amount == 0:
                sitem.timesBought = sitem.timesBought + 1
                sitem.save()
                parent_ob.credits = parent_ob.credits + sitem.credits
                parent_ob.save()
                return Response(parent_ob)

        url = "https://api.paymongo.com/v1/payment_intents"

        payload = {"data": {"attributes": {
                    "amount": amount,
                    "payment_method_allowed": ["card"],
                    "payment_method_options": {"card": {"request_three_d_secure": "any"}},
                    "currency": "PHP"
                }}}
        headers = paymongo_headers

        response = requests.request("POST", url, json=payload, headers=headers)

        print(response.text)
        res = json.loads(response.text)['data']

        client_key = res['attributes']['client_key']

        parent = Parent.objects.get(id=parent_id)
        parent.first_buy = True
        parent.save()

        # credits = 0
        #
        # if(amount == 54900):
        #     credits = 1
        # elif(amount == 499900):
        #     credits = 10
        # elif(amount == 719900):
        #     credits = 20

        # Modify amount here --> FOR NOW

        timezone.activate(pytz.timezone("Asia/Manila"))
        transaction = PayMongoTransaction(parent=parent, client_key=client_key, credits=credits, amount=amount, date=timezone.localtime(timezone.now()))
        transaction.save()

        # Shop Item stats
        sitem.timesBought = sitem.timesBought + 1
        sitem.save()

        return Response(client_key)

class PayMongoAPILegacy(APIView):
    def post(self, request, format=None):
        amount = int(request.data['amount']) * 100
        parent_id = request.data['parent_id']

        url = "https://api.paymongo.com/v1/payment_intents"

        payload = {"data": {"attributes": {
                    "amount": amount,
                    "payment_method_allowed": ["card"],
                    "payment_method_options": {"card": {"request_three_d_secure": "any"}},
                    "currency": "PHP"
                }}}
        headers = paymongo_headers

        response = requests.request("POST", url, json=payload, headers=headers)

        res = json.loads(response.text)['data']

        client_key = res['attributes']['client_key']

        parent = Parent.objects.get(id=parent_id)

        credits = 0

        if(amount == 54900):
            credits = 1
        elif(amount == 499900):
            credits = 10
        elif(amount == 719900):
            credits = 20

        # Modify amount here --> FOR NOW

        transaction = PayMongoTransaction(parent=parent, client_key=client_key, credits=credits, amount=amount)
        transaction.save()

        return Response(client_key)

class VerifyPayMongoAPI(APIView):
    def post(self, request, format=None):
        client_key = request.data['client_key']
        payment_intent = request.data['payment_intent']
        parent_id = request.data['parent_id']

        try:
            parent = Parent.objects.get(id=parent_id)
            transaction = PayMongoTransaction.objects.get(parent=parent, client_key=client_key)

            url = 'https://api.paymongo.com/v1/payment_intents/'+payment_intent+'?client_key='+client_key

            payload={}
            # headers = {
            # 'Authorization': 'Basic cGtfdGVzdF9MaUJpWXRoeDFEMzZoUVlWY1BTUkIyTUo6'
            # }
            headers = paymongo_headers
            response = requests.request("GET", url, headers=headers, data=payload)
            res = json.loads(response.text)

            if(transaction.status):
                return Response(False)
            else:
                if(res['data']['attributes']['status'] == 'succeeded'):
                    parent.credits += transaction.credits
                    transaction.status = True
                    parent.save()
                    transaction.save()
                    return Response(True)

        except:
            return Response(False)

        return Response(False)
