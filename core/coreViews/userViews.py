from rest_framework import permissions
from rest_framework.views import APIView
import requests
import json
import random
import os 
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from core.extra_functions import getStartDateAndEndDateOfWeek, displayErrors
from django.utils import timezone
import datetime
import pytz

from core.serializers import (
    UserSerializer,
    GroupSerializer,
    ParentSerializer,
    TutorSerializer,
    ChildSerializer,
    RequestsSerializer,
    FeedbackSerializer,
    SessionSerializer,
    ConversationSerializer,
    MessageSerializer,
    FavouriteTutorSerializer,
    PayMongoTransactionSerializer,
    SourcePayMongoTransactionSerializer,
    BrankasTransactionSerializer,
    AvailableDaysSerializer,
    SubjectSerializer,
    AdminSettingSerializer,
    ParentSettingSerializer,
    TutorSettingSerializer,
    ParentNotificationSerializer,
    TutorNotificationSerializer,
    TutorSubjectSerializer,
    TutorApplicationSerializer,
    TutorPayoutSerializer,
    ShopItemSerializer,
    AdminTutorMessageSerializer,
    AdminTutorConversationSerializer,
    AdminParentMessageSerializer,
    AdminParentConversationSerializer,
    )

from core.models import (
    Parent,
    Tutor,
    Child,
    Requests,
    Feedback,
    Session,
    Conversation,
    Message,
    FavouriteTutor,
    PayMongoTransaction,
    SourcePayMongoTransaction,
    BrankasTransaction,
    AvailableDays,
    Subject,
    AdminSetting,
    ParentSetting,
    TutorSetting,
    ParentNotification,
    TutorNotification,
    TutorSubject,
    TutorApplication,
    TutorPayout,
    ShopItem,
    AdminTutorMessage,
    AdminTutorConversation,
    AdminParentMessage,
    AdminParentConversation,
    )

from core.ws import sendBroadcast


# reading .env file


class ParentNotFirstTimeUser(APIView):
    """
    POST:
    Description: Makes the parent not a first time user
    Input:
    {
        "parent_id": id of parent object
    }
    Output:
    {
        "parent": parent object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['parent'] = None
        parent_id = request.data['parent_id']

        try:
            parent_ob = Parent.objects.get(id=parent_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent not found"
            return Response(return_info)

        if (parent_ob.first_time_user == False):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent account already a non-first time user"
            return Response(return_info)

        parent_ob.first_time_user = False
        parent_ob.save()
        parent_ob_ser = ParentSerializer(parent_ob)
        return_info['parent'] = parent_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully made parent account of " + parent_ob.first_name + " a non-first time user"

        return Response(return_info)

class TutorNotFirstTimeUser(APIView):
    """
    POST:
    Description: Makes the Tutor not a first time user
    Input:
    {
        "tutor_id": id of parent object
    }
    Output:
    {
        "tutor": parent object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['tutor'] = None
        tutor_id = request.data['tutor_id']

        try:
            tutor_ob = Tutor.objects.get(id=tutor_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Tutor not found"
            return Response(return_info)

        if (tutor_ob.first_time_user == False):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Tutor account already a non-first time user"
            return Response(return_info)

        tutor_ob.first_time_user = False
        tutor_ob.save()
        tutor_ob_ser = TutorSerializer(tutor_ob)
        return_info['tutor'] = tutor_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully made the tutor account of " + tutor_ob.first_name + " a non-first time user"

        return Response(return_info)


class AllParentDetails(APIView):
    """
    POST:
    Description: get everything of parent
    Input:
    {
    "parent_id": id of parent
    }
    Output:
    {
        "parent": {
            "username": string,
            "first_name": string,
            "last_name": string,
            "email": string,
            "credits": float,
            "status": boolean
        },
        "children": [
            {
                "parent": id of parent,
                "first_name": string,
                "last_name": string,
                "age": int,
                "year_level": string,
                "school": string
            }
        ],
        "pending_requests": [
            "request": {
                request object
            },
            "child": {
                child object
            },
            "available_days": [
                {
                    available day objects
                }
                ...
            ],
            "subject": {
                subject object
            }
            ...
        ],
        "accepted_requests": [
            "request": {
                request object
            },
            "child": {
                child object
            },
            "session":{
                session object
            }
            ,
            "subject": {
                subject object
            },
            "tutor":{
                tutor object
            }
            ...
        ],
        "finished_requests": [
            "request": {
                request object
            },
            "child": {
                child object
            },
            "session":{
                session object
            }
            ,
            "subject": {
                subject object
            },
            "tutor":{
                tutor object
            }
            ...
        ],
        "FavouriteTutor": [
            {
                "parent": id of parent,
                "tutor": id of tutor
            }
        ],
        "transactions": [
            {
                "parent": id of parent,
                "credits": float,
                "amount": float (How much it cost in PHP to add the credits)
                "method": string (wait for manny to respond to discord question)
            }
        ],
        "subjects": [
            {
                "id": id of parent,
                "subject_field": string
            }
        ],
        "settings" : [
            {
                "id": id of parent settings,
                "parent": id of parent,
                "field_name": string,
                "value": string
            }
        ],
        "admin_setting": [
            {
                "id": id of admin setting,
                "field_name": string,
                "value": string
            },
        ],
        "shop_items": {
            [
                shop item objects
            ]
        },
        "conversations":{
            "admin":
    			{
    				"id": id of adminparentconversation object,
    				"parent": id of parent
    			},
    		"active": [
        		{
        			"conversation": conversation object,
        			"parent": parent object,
        			"tutor": tutor object
        		}
    		],
    		"inactive": [
        		{
        			"conversation": conversation object,
        			"parent": parent object,
        			"tutor": tutor object
        		}
    		]
        }
    }
    """

    def post(self, request, format=None):

        parent_info = {}

        parent_id = request.data['parent_id']
        # date = request.data['date']

        #get parent object
        parent = Parent.objects.get(id=parent_id)
        parent_serializer = ParentSerializer(parent)

        parent_info['parent'] = parent_serializer.data

        #get all parents children
        children = Child.objects.filter(parent=parent_id)
        child_serializer = ChildSerializer(children, many=True)

        parent_info['children'] = child_serializer.data

        #get pending requests based on date
        queryset = Requests.objects.filter(parent=parent_id, status='pending').order_by("time_created")
        serializer_class = RequestsSerializer(queryset, many=True)

        # Add Child, Available Days, and Subject Info
        pending_reqlist = []
        for r in serializer_class.data:
            preq_info = {}
            c_ob = Child.objects.get(id=r['child'])
            ad_ob = AvailableDays.objects.filter(request=r['id'])
            sub_ob = Subject.objects.get(id=r['subject'])

            c_ob_serializer = ChildSerializer(c_ob)
            ad_ob_serializer = AvailableDaysSerializer(ad_ob, many=True)
            sub_ob_serializer = SubjectSerializer(sub_ob)

            preq_info['child'] = c_ob_serializer.data
            preq_info['request'] = r
            preq_info['available_days'] = ad_ob_serializer.data
            preq_info['subject'] = sub_ob_serializer.data
            pending_reqlist.append(preq_info)

        parent_info['pending_requests'] = pending_reqlist
        # parent_info['pending_requests'] = serializer_class.data

        #get accepted requests based on date
        queryset = Requests.objects.filter(parent=parent_id).filter(status='accepted').order_by('time_created')
        serializer_class = RequestsSerializer(queryset, many=True)

        AcceptedRequestsSet = []

        for r in serializer_class.data:
            # if r['start_date_time'].split("T")[0] == date:
            try:
                preq_info = {}
                c_ob = Child.objects.get(id=r['child'])
                sub_ob = Subject.objects.get(id=r['subject'])
                session = Session.objects.get(request=r['id'])

                c_ob_serializer = ChildSerializer(c_ob)
                sub_ob_serializer = SubjectSerializer(sub_ob)
                session_serializer = SessionSerializer(session)

                tutor_ob = Tutor.objects.get(id=session_serializer.data['tutor'])
                tutor_serializer = TutorSerializer(tutor_ob)

                preq_info['child'] = c_ob_serializer.data
                preq_info['request'] = r
                preq_info['subject'] = sub_ob_serializer.data
                preq_info['session'] = session_serializer.data
                preq_info['tutor'] = tutor_serializer.data

                AcceptedRequestsSet.append(preq_info)
            except Exception as e:
                print(e)
                pass

            # session = Session.objects.get(request=r['id'])
            # r['zoom_link'] = session.zoom_link
            #r['active'] = session.active #talk about this with manny later on

        parent_info['accepted_requests'] = AcceptedRequestsSet

        #get finished requests based on date
        queryset = Requests.objects.filter(parent=parent_id).filter(status='finished').order_by('-time_created')[:20]
        serializer_class = RequestsSerializer(queryset, many=True)

        FinishedRequestsSet = []

        for r in serializer_class.data:
            preq_info = {}
            c_ob = Child.objects.get(id=r['child'])
            sub_ob = Subject.objects.get(id=r['subject'])
            session = Session.objects.get(request=r['id'])

            c_ob_serializer = ChildSerializer(c_ob)
            sub_ob_serializer = SubjectSerializer(sub_ob)
            session_serializer = SessionSerializer(session)

            tutor_ob = Tutor.objects.get(id=session_serializer.data['tutor'])
            tutor_serializer = TutorSerializer(tutor_ob)

            preq_info['child'] = c_ob_serializer.data
            preq_info['request'] = r
            preq_info['subject'] = sub_ob_serializer.data
            preq_info['session'] = session_serializer.data
            preq_info['tutor'] = tutor_serializer.data

            FinishedRequestsSet.append(preq_info)

        parent_info['finished_requests'] = FinishedRequestsSet

        #get favourite tutors
        queryset = FavouriteTutor.objects.filter(parent=parent_id)
        serializer_class = FavouriteTutorSerializer(queryset, many=True)

        fav_tutors = []

        for r in serializer_class.data:
            preq_info = {}
            tut_ob = Tutor.objects.get(id=r['tutor'])

            tut_ob_serializer = TutorSerializer(tut_ob)

            # preq_info['fav_tutor'] = r
            preq_info['tutor'] = tut_ob_serializer.data

            fav_tutors.append(preq_info)

        parent_info['FavouriteTutor'] = fav_tutors

        #get all transactions
        all_transactions = []

        queryset = PayMongoTransaction.objects.filter(parent=parent_id).order_by('-date')[:10]
        serializer_class = PayMongoTransactionSerializer(queryset, many=True)
        all_transactions += serializer_class.data

        # queryset = SourcePayMongoTransaction.objects.filter(parent=parent_id).order_by('-date')[:10]
        # serializer_class = SourcePayMongoTransactionSerializer(queryset, many=True)
        # all_transactions += serializer_class.data

        # queryset = BrankasTransaction.objects.filter(parent=parent_id).order_by('-date')[:10]
        # serializer_class = BrankasTransactionSerializer(queryset, many=True)
        # all_transactions += serializer_class.data

        parent_info['transactions'] = all_transactions

        #get all subjects
        queryset = Subject.objects.all()
        serializer_class = SubjectSerializer(queryset, many=True)

        parent_info['subjects'] = serializer_class.data

        #get all settings
        queryset = ParentSetting.objects.filter(parent=parent_id)
        serializer_class = ParentSettingSerializer(queryset, many=True)

        parent_info['settings'] = serializer_class.data

        queryset = AdminSetting.objects.all()
        serializer_class = AdminSettingSerializer(queryset, many=True)

        parent_info['admin_settings'] = serializer_class.data

        queryset = ShopItem.objects.filter(archived=False)
        serializer_class = ShopItemSerializer(queryset, many=True)

        parent_info['shop_items'] = serializer_class.data

        conversation_dict = {}
        conversation_dict['admin'] = []
        conversation_dict['active'] = []
        conversation_dict['inactive'] = []

        convo_ob = {}
        ap_con = AdminParentConversation.objects.get(parent=parent_id)
        apcon_ser = AdminParentConversationSerializer(ap_con)
        convo_ob['conversation'] = apcon_ser.data
        message =  AdminParentMessage.objects.filter(ap_conversation=ap_con.id).order_by('-time_sent').first()
        mes_ser = AdminParentMessageSerializer(message)
        convo_ob['latest_message'] = mes_ser.data
        conversation_dict['admin'] = convo_ob

        active_list = []
        active_convo = Conversation.objects.filter(parent=parent_id, active=True)
        for convo in active_convo:
            convo_ob = {}
            tutor = Tutor.objects.get(id=convo.tutor.id)
            convo_serializer = ConversationSerializer(convo)
            convo_ob['conversation'] = convo_serializer.data
            message =  Message.objects.filter(conversation=convo.id).order_by('-time_sent').first()

            par_ser = ParentSerializer(parent)
            tur_sur = TutorSerializer(tutor)
            mes_ser = MessageSerializer(message)

            convo_ob['parent'] = par_ser.data
            convo_ob['tutor'] = tur_sur.data
            convo_ob['latest_message'] = mes_ser.data

            active_list.append(convo_ob)
        conversation_dict['active'] = active_list

        inactive_list = []
        inactive_convo = Conversation.objects.filter(parent=parent_id, active=False)
        for convo in inactive_convo:
            convo_ob = {}
            tutor = Tutor.objects.get(id=convo.tutor.id)
            convo_serializer = ConversationSerializer(convo)
            convo_ob['conversation'] = convo_serializer.data
            message =  Message.objects.filter(conversation=convo.id).order_by('-time_sent').first()

            par_ser = ParentSerializer(parent)
            tur_sur = TutorSerializer(tutor)
            mes_ser = MessageSerializer(message)

            convo_ob['parent'] = par_ser.data
            convo_ob['tutor'] = tur_sur.data
            convo_ob['latest_message'] = mes_ser.data

            inactive_list.append(convo_ob)
        conversation_dict['inactive'] = inactive_list

        parent_info['conversations'] = conversation_dict

        return Response(parent_info)

class AllTutorDetails(APIView):
    """
    POST:
    Description: get everything of tutor
    Input:
    {
    "tutor_id": id of tutor
    }
    Output:
    {
        "tutor": {
            "username": String,
            "first_name": String,
            "last_name": String,
            "email": String,
            "school": String,
            "course": String,
            "achievements": String,
            "rating": float,
            "subjects": String,
            "zoominfo": String,
            "status": boolean,
            "phone": String,
            "picture": String
        },
        "accepted_requests": [
            "request": {
                request object
            },
            "child": {
                child object
            },
            "session":{
                session object
            }
            ,
            "subject": {
                subject object
            },
            "tutor":{
                tutor object
            }
            ...
        ],
        "finished_requests": [
            "request": {
                request object
            },
            "child": {
                child object
            },
            "session":{
                session object
            }
            ,
            "subject": {
                subject object
            },
            "tutor":{
                tutor object
            }
            ...
        ],
        "number_of_students": int,
        "total_hours": float,
        "tutor_earning_month": float,
        "tutor_earning_all_time": float,
        "pending_requests": [
            {
                "parent": {
                    "id": id of parent,
                    "username": string,
                    "first_name": string,
                    "last_name": string,
                    "email": string,
                    "credits": float,
                    "status": string,
                    "phone": string,
                    "picture": string
                },
                "child": {
                    "id": id of child,
                    "parent": id of parent,
                    "first_name": string,
                    "last_name": string,
                    "age": integer,
                    "year_level": integer,
                    "school": string
                },
                "request": {
                    request object
                },
                "available_days": [
                    {
                        "id": id of available day,
                        "request": id of request,
                        "start_date_time": datetime,
                        "end_date_time": datetime,
                        "time": float
                    }
                    ...
                ]
            }
            ...
        ]
        "favorite_pending_requests": [
            {
                "parent": {
                    "id": id of parent,
                    "username": string,
                    "first_name": string,
                    "last_name": string,
                    "email": string,
                    "credits": float,
                    "status": string,
                    "phone": string,
                    "picture": string
                },
                "child": {
                    "id": id of child,
                    "parent": id of parent,
                    "first_name": string,
                    "last_name": string,
                    "age": integer,
                    "year_level": integer,
                    "school": string
                },
                "request": {
                    request object
                },
                "available_days": [
                    {
                        "id": id of available day,
                        "request": id of request,
                        "start_date_time": datetime,
                        "end_date_time": datetime,
                        "time": float
                    }
                    ...
                ]
            }
            ...
        ]
        "settings": [
            {
                "id": id of tutor settings,
                "tutor": id of tutor,
                "field_name": string,
                "value": string
            },
            ...
        ],
        "subjects": [
            {
                "id": id of tutor subject,
                "tutor": id of tutor,
                "subject": id of subject
            },
            ...
        ],
        "admin_settings": [
            {
                "id": id of admin settings,
                "field_name": string,
                "value": string
            },
            ...
        ],
        "conversations":{
            "admin":
    			{
    				"id": id of admintutorconversation object,
    				"parent": id of parent
    			},
    		"active": [
        		{
        			"conversation": conversation object,
        			"parent": parent object,
        			"tutor": tutor object
        		}
    		],
    		"inactive": [
        		{
        			"conversation": conversation object,
        			"parent": parent object,
        			"tutor": tutor object
        		}
    		]
        }
    }
    """
    def post(self, request, format=None):

        tutor_info = {}

        tutor_id = request.data['tutor_id']

        #Profile - Tutor contact details and subjects they teach
        #get tutor object
        tutor = Tutor.objects.get(id=tutor_id)
        tutor_serializer = TutorSerializer(tutor)

        tutor_info['tutor'] = tutor_serializer.data
        accepted_queryset = []
        # We get session instead because the tutor is in the session not the request
        session_queryset = Session.objects.filter(tutor=tutor_id, active="True").order_by("start_date_time")
        session_queryset_serializer = SessionSerializer(session_queryset, many=True)
        for r in session_queryset_serializer.data:
            preq_info = {}

            request_ob = Requests.objects.get(id=r['request'])
            c_ob = Child.objects.get(id=request_ob.child.id)
            sub_ob = Subject.objects.get(id=request_ob.subject.id)

            request_ob_serializer = RequestsSerializer(request_ob)
            c_ob_serializer = ChildSerializer(c_ob)
            sub_ob_serializer = SubjectSerializer(sub_ob)

            preq_info['child'] = c_ob_serializer.data
            preq_info['request'] = request_ob_serializer.data
            preq_info['subject'] = sub_ob_serializer.data
            preq_info['session'] = r
            preq_info['tutor'] = tutor_serializer.data

            accepted_queryset.append(preq_info)

        #Upcoming Sessions - Accepted Requests
        # queryset = Requests.objects.filter(tutor=tutor_id).filter(status='accepted')
        # accepted_serializer_class = RequestsSerializer(queryset, many=True)
        # AcceptedRequestsSet = []
        #
        # for r in accepted_queryset:
        #     # if r['start_date_time'].split("T")[0] == date:
        #     AcceptedRequestsSet.append(r)
        #
        #     session = Session.objects.get(request=r['id'])
        #     r['zoom_link'] = session.zoom_link

        tutor_info['accepted_requests'] = accepted_queryset

        #Session History - Accomplished Requests
        #get finished requests
        finished_queryset = []
        session_queryset = Session.objects.filter(tutor=tutor_id, active="False").order_by("-start_date_time")
        session_queryset_serializer = SessionSerializer(session_queryset, many=True)
        for r in session_queryset_serializer.data:
            request_ob = Requests.objects.get(id=r['request'])
            if request_ob.status == 'finished':
                preq_info = {}

                c_ob = Child.objects.get(id=request_ob.child.id)
                sub_ob = Subject.objects.get(id=request_ob.subject.id)

                request_ob_serializer = RequestsSerializer(request_ob)
                c_ob_serializer = ChildSerializer(c_ob)
                sub_ob_serializer = SubjectSerializer(sub_ob)

                preq_info['child'] = c_ob_serializer.data
                preq_info['request'] = request_ob_serializer.data
                preq_info['subject'] = sub_ob_serializer.data
                preq_info['session'] = r
                preq_info['tutor'] = tutor_serializer.data

                finished_queryset.append(preq_info)

        # queryset = Requests.objects.filter(tutor_email=tutor.email).filter(status='finished')
        # finished_serializer_class = RequestsSerializer(queryset, many=True)

        # FinshedRequestsSet = []
        #
        # for r in finished_queryset:
        #     # if r['start_date_time'].split("T")[0] == date:
        #     FinshedRequestsSet.append(r)
        #
        #     session = Session.objects.get(request=r['id'])
        #     r['zoom_link'] = session.zoom_link

        tutor_info['finished_requests'] = finished_queryset

        #Metrics - Average Tutor Rating, No. of students taken, total hours, total earning (for this month and all-time)
        #Average tutor rating is a field in tutor already, just have to adjust it everytime feedback is made

        #number of students taken
        childrenSet = []

        for r in accepted_queryset:
            if r['child'] not in childrenSet:
                childrenSet.append(r['child'])

        for r in finished_queryset:
            if r['child'] not in childrenSet:
                childrenSet.append(r['child'])

        tutor_info['number_of_students'] = len(childrenSet)

        #total hours (only looks at finished requests)
        total_hours = 0
        session_list = []

        for r in finished_queryset:
            total_hours += r['request']['time']
            session_list.append(r['session'])

        tutor_info['total_hours'] = total_hours

        #total earning month and all-time

        tutor_earning_month = 0

        timezone.activate(pytz.timezone("Asia/Manila"))
        for r in session_list:
            if r['end_date_time'].split('-')[1] == str(timezone.localtime(timezone.now()).month):
                req_ob = Requests.objects.get(id=r['request'])
                tutor_earning_month += req_ob.time * 300

        tutor_info['tutor_earning_month'] = tutor_earning_month
        tutor_info['tutor_earning_all_time'] = total_hours * 300

        #Requests - Not yet accepted requests that are available
        # CASE 1: get all pending requests that have no favurites
        queryset = Requests.objects.filter(status='pending', is_favourite=False, fav_tutor=None).order_by("-time_created")
        # serializer_class = RequestsSerializer(queryset, many=True)

        # Get subjects taught by the tutor
        subject_list = []
        t_subs = TutorSubject.objects.filter(tutor=tutor_id)
        for t_sub in t_subs:
            subject_list.append(t_sub.subject)

        pending_reqlist = []
        for r in queryset:
            if tutor not in r.declined_tutors.all():
                # Filter out requests not taught by a tutor
                if r.subject in subject_list:
                    preq_info = {}
                    p_ob = Parent.objects.get(id=r.parent.id)
                    c_ob = Child.objects.get(id=r.child.id)
                    ad_ob = AvailableDays.objects.filter(request=r.id)
                    sub_ob = Subject.objects.get(id=r.subject.id)

                    p_ob_serializer = ParentSerializer(p_ob)
                    c_ob_serializer = ChildSerializer(c_ob)
                    ad_ob_serializer = AvailableDaysSerializer(ad_ob, many=True)
                    sub_ob_serializer = SubjectSerializer(sub_ob)
                    request_serializer = RequestsSerializer(r)

                    preq_info['parent'] = p_ob_serializer.data
                    preq_info['child'] = c_ob_serializer.data
                    preq_info['request'] = request_serializer.data
                    preq_info['available_days'] = ad_ob_serializer.data
                    preq_info['subject'] = sub_ob_serializer.data
                    pending_reqlist.append(preq_info)

        tutor_info['pending_requests'] = pending_reqlist

        pending_reqlist = []
        # CASE 2: Parents who made requests to a certain person (i.e. the tutor itself)
        queryset = Requests.objects.filter(status='pending', is_favourite=True, fav_tutor=tutor_id).order_by("-time_created")
        # serializer_class = RequestsSerializer(queryset, many=True)

        pending_reqlist = []
        for r in queryset:
            if tutor not in r.declined_tutors.all():
                if r.subject in subject_list:
                    preq_info = {}
                    p_ob = Parent.objects.get(id=r.parent.id)
                    c_ob = Child.objects.get(id=r.child.id)
                    ad_ob = AvailableDays.objects.filter(request=r.id)
                    sub_ob = Subject.objects.get(id=r.subject.id)

                    p_ob_serializer = ParentSerializer(p_ob)
                    c_ob_serializer = ChildSerializer(c_ob)
                    ad_ob_serializer = AvailableDaysSerializer(ad_ob, many=True)
                    sub_ob_serializer = SubjectSerializer(sub_ob)
                    request_serializer = RequestsSerializer(r)

                    preq_info['parent'] = p_ob_serializer.data
                    preq_info['child'] = c_ob_serializer.data
                    preq_info['request'] = request_serializer.data
                    preq_info['available_days'] = ad_ob_serializer.data
                    preq_info['subject'] = sub_ob_serializer.data
                    pending_reqlist.append(preq_info)

        # CASE 3: Parents who made the requests to their favourite tutors
        queryset = Requests.objects.filter(status='pending', is_favourite=True, fav_tutor=None).order_by("-time_created")
        # serializer_class = RequestsSerializer(queryset, many=True)

        for r in queryset:
            #check if request made by parent is favourited by current tutor
            preq_info = {}

            p_ob = Parent.objects.get(id=r.parent.id)
            fav_tutor_count = FavouriteTutor.objects.filter(parent=p_ob.id, tutor=tutor.id).count()
            if fav_tutor_count == 1 and tutor not in r.declined_tutors.all():
                if r.subject in subject_list:
                    c_ob = Child.objects.get(id=r.child.id)
                    ad_ob = AvailableDays.objects.filter(request=r.id)
                    sub_ob = Subject.objects.get(id=r.subject.id)

                    p_ob_serializer = ParentSerializer(p_ob)
                    c_ob_serializer = ChildSerializer(c_ob)
                    ad_ob_serializer = AvailableDaysSerializer(ad_ob, many=True)
                    sub_ob_serializer = SubjectSerializer(sub_ob)
                    request_serializer = RequestsSerializer(r)

                    preq_info['parent'] = p_ob_serializer.data
                    preq_info['child'] = c_ob_serializer.data
                    preq_info['request'] = request_serializer.data
                    preq_info['available_days'] = ad_ob_serializer.data
                    preq_info['subject'] = sub_ob_serializer.data
                    pending_reqlist.append(preq_info)

        tutor_info['favorite_pending_requests'] = pending_reqlist

        queryset = TutorSetting.objects.filter(tutor=tutor_id)
        serializer_class = TutorSettingSerializer(queryset, many=True)

        tutor_info['settings'] = serializer_class.data

        queryset = TutorSubject.objects.filter(tutor=tutor_id)
        serializer_class = TutorSubjectSerializer(queryset, many=True)

        tutor_info['subjects'] = serializer_class.data

        queryset = AdminSetting.objects.all()
        serializer_class = AdminSettingSerializer(queryset, many=True)

        tutor_info['admin_settings'] = serializer_class.data

        conversation_dict = {}
        conversation_dict['active'] = []
        conversation_dict['inactive'] = []

        convo_ob = {}
        at_con = AdminTutorConversation.objects.get(tutor=tutor_id)
        atcon_ser = AdminTutorConversationSerializer(at_con)
        convo_ob['conversation'] = atcon_ser.data
        message =  AdminTutorMessage.objects.filter(at_conversation=at_con.id).order_by('-time_sent').first()
        mes_ser = AdminTutorMessageSerializer(message)
        convo_ob['latest_message'] = mes_ser.data
        conversation_dict['admin'] = convo_ob

        active_list = []
        active_convo = Conversation.objects.filter(tutor=tutor_id, active=True)
        for convo in active_convo:
            convo_ob = {}
            convo_serializer = ConversationSerializer(convo)
            convo_ob['conversation'] = convo_serializer.data
            parent = Parent.objects.get(id=convo.parent.id)
            message =  Message.objects.filter(conversation=convo.id).order_by('-time_sent').first()

            par_ser = ParentSerializer(parent)
            tur_sur = TutorSerializer(tutor)
            mes_ser = MessageSerializer(message)

            convo_ob['parent'] = par_ser.data
            convo_ob['tutor'] = tur_sur.data
            convo_ob['latest_message'] = mes_ser.data
            active_list.append(convo_ob)
        conversation_dict['active'] = active_list

        inactive_list = []
        inactive_convo = Conversation.objects.filter(tutor=tutor_id, active=False)
        for convo in inactive_convo:
            convo_ob = {}
            convo_serializer = ConversationSerializer(convo)
            convo_ob['conversation'] = convo_serializer.data
            parent = Parent.objects.get(id=convo.parent.id)
            message =  Message.objects.filter(conversation=convo.id).order_by('-time_sent').first()

            par_ser = ParentSerializer(parent)
            tur_sur = TutorSerializer(tutor)
            mes_ser = MessageSerializer(message)

            convo_ob['parent'] = par_ser.data
            convo_ob['tutor'] = tur_sur.data
            convo_ob['latest_message'] = mes_ser.data
            inactive_list.append(convo_ob)
        conversation_dict['inactive'] = inactive_list

        tutor_info['conversations'] = conversation_dict

        return Response(tutor_info)

class SpecificTutorView(APIView):
    """
    POST:
    Description: Returns a specific tutor along with their total number of hours they have tutored
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "number_of_students": integer,
        "total_hours": integer,
        "tutor": {
            "id": id of tutor,
            "username": string,
            "first_name": string,
            "last_name": string,
            "email": string,
            "school": string,
            "course": string,
            "achievements": string,
            "rating": float,
            "zoominfo": string,
            "status": boolean,
            "phone": string,
            "picture": string
        }
    }
    """
    def post(self, request, format=None):
        return_info = {}
        tutor_id = request.data['tutor_id']

        accepted_queryset = []
        # We get session instead because the tutor is in the session not the request
        session_queryset = Session.objects.filter(tutor=tutor_id, active="True")
        session_queryset_serializer = SessionSerializer(session_queryset, many=True)
        for r in session_queryset_serializer.data:
            request_ob = Requests.objects.get(id=r['request'])
            request_ob_serializer = RequestsSerializer(request_ob)
            accepted_queryset.append(request_ob_serializer.data)

        finished_queryset = []
        session_queryset = Session.objects.filter(tutor=tutor_id, active="False")
        session_queryset_serializer = SessionSerializer(session_queryset, many=True)
        for r in session_queryset_serializer.data:
            request_ob = Requests.objects.get(id=r['request'])
            request_ob_serializer = RequestsSerializer(request_ob)
            if request_ob.status == 'finished':
                finished_queryset.append(request_ob_serializer.data)

        childrenSet = []

        for r in accepted_queryset:
            if r['child'] not in childrenSet:
                childrenSet.append(r['child'])

        for r in finished_queryset:
            if r['child'] not in childrenSet:
                childrenSet.append(r['child'])

        return_info['number_of_students'] = len(childrenSet)

        total_hours = 0
        session_list = []

        for r in finished_queryset:
            total_hours += r['time']
            session_ob = Session.objects.get(request=r['id'])
            session_ob_serializer = SessionSerializer(session_ob)
            session_list.append(session_ob_serializer.data)

        return_info['total_hours'] = total_hours

        queryset = Tutor.objects.get(id=tutor_id)
        serializer_class = TutorSerializer(queryset)
        return_info['tutor'] = serializer_class.data

        # test_data = serializer_class.data
        #
        # time_query = Requests.objects.filter(tutor=tutor_id, status='finished')
        # time_serializer = RequestsSerializer(time_query, many=True)
        #
        # total_time = 0
        #
        # for r in time_serializer.data:
        #     if r['status'] == 'active':
        #         total_time += r['time']

        # test_data['total_time'] = total_time

        return Response(return_info)

class TutorPayoutAPI(APIView):
    """
    POST:
    Description: Get tutor payout details separated by week
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "tutorpayouts": [
            {
                "amountDue": int,
                "week_bound": String (ex. 2020-11-21/2020-11-27),
                "sessions": [
                    {
                        "student": id of child,
                        "payout": int,
                        "time": int,
                        "end_date_time": DateTime (ex. 2020-11-22T21:34:00+08:00),
                        "subject": id of subject,
                        "year_level": String
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['tutorpayouts'] = []

        tutor_id = request.data['tutor_id']

        tutor_payouts = TutorPayout.objects.filter(tutor=tutor_id)
        tutor_payouts_serializer = TutorPayoutSerializer(tutor_payouts, many=True)

        for tutor_payout in tutor_payouts_serializer.data:
            week_info = {}

            amountDue = 0
            week_bound = tutor_payout['week_bracket']
            sessions = tutor_payout['session']
            session_info_list = []

            for session_id in sessions:
                session = Session.objects.get(id=session_id)
                request_id = session.request.id
                request_ob = Requests.objects.get(id=request_id)

                child = Child.objects.get(id=request_ob.child.id)

                session_info = {}
                session_info['student'] = child.id
                session_info['payout'] = request_ob.time*300
                session_info['time'] = request_ob.time
                session_info['end_date_time'] = session.end_date_time
                session_info['subject'] = request_ob.subject.id
                session_info['year_level'] = child.year_level

                session_info_list.append(session_info)

                amountDue = amountDue + (request_ob.time * 300)

            week_info['amountDue'] = amountDue
            week_info['week_bound'] = week_bound
            week_info['sessions'] = session_info_list
            week_info['isPaid'] = tutor_payout['isPaid']
            week_info['photo'] = tutor_payout['photo']

            return_info['tutorpayouts'].append(week_info)

        return Response(return_info)

class AddFavouriteTutor(APIView):
    """
    POST:
    Description: Add a tutor as a favourite tutor
    Input:
    {
    "parent_id": id of parent
    "tutor_id": id of tutor
    }
    Output:
    {
    "parent_id": id of parent
    "tutor_id": id of tutor
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        tutor_id = request.data['tutor_id']

        #check if they already favourited the tutor
        check_match = FavouriteTutor.objects.filter(parent=parent_id).filter(tutor=tutor_id)

        if not check_match:
            data = {
            "parent": parent_id,
            "tutor": tutor_id
            }

            serializer_class = FavouriteTutorSerializer(data=data)
            if serializer_class.is_valid():
                serializer_class.save()
                return Response(serializer_class.data)

        else:
            return Response ('Tutor is already favourited')

class ParentMakeRequest(APIView):
    """
    POST:
    Description: Parent makes a request
    Input:
    {
        "parent_id": id of parent,
        "child_id": id of child,
        "extra_files": String,
        "is_favourite": boolean,
        "subject": id of subject,
        "topics": String,
        "special_request": String,
        "time": Integer,
        "available_days": List of objects [
                {
                    "start_date_time": Datetime,
                    "end_date_time": Datetime
                }
            ],
        "fav_tutor": id of tutor
    }
    Output:
    {
        "return_status": string,
        "return_message": string
        "request": {
            "parent": id of parent,
            "child": id of child,
            "tutor": id of tutor,
            "time": integer,
            "extra_files": String,
            "status": "pending",
            "is_favourite": boolean,
            "subject": id of subject,
            "topics": String,
            "special_request": String
        },
        "available_days": [
            {
                "request": id of request,
                "start_date_time": DateTime,
                "end_date_time": DateTime
            }
        ]
    }
    """
    def post(self, request, format=None):
        try:
            return_info = {}
            return_info['return_status'] = ""
            return_info['return_message'] = ""

            parent_id = request.data['parent_id']
            child_id = request.data['child_id']
            time = request.data['time']
            available_days = request.data['available_days']
            extra_files = request.data['extra_files']
            is_favourite = request.data['is_favourite']
            subject = request.data['subject']
            topics = request.data['topics']
            special_request = request.data['special_request']
            available_days = request.data['available_days']
            fav_tutor = request.data['fav_tutor']

            parent = Parent.objects.get(id=parent_id)
            parent_credits = parent.credits

            child = Child.objects.get(id=child_id)

            #check all pending requests to check if parent has enough credits to make more
            made_requests = Requests.objects.filter(parent=parent.id).filter(status='pending')
            made_requests_serializer = RequestsSerializer(made_requests, many=True)

            #for checking if new request interferes with accepted requests
            accepted_requests = Requests.objects.filter(parent=parent.id).filter(status='accepted')
            accepted_requests_serializer = RequestsSerializer(accepted_requests, many=True)

            made_requests_count = 0
            total_made_requests_cost = 0

            # if fav_tutor == "" and is_favourite == "true":
            #     return_info['return_status'] = "error"
            #     return_info['return_message'] = "Error: Cannot have a favourite tutor if the request made is for non-favourite tutors"
            #     return Response(return_info)

            if fav_tutor != "" and is_favourite == True:
                fav_count = FavouriteTutor.objects.filter(parent=parent_id, tutor=fav_tutor).count()
                if fav_count == 0:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Favourite tutor id sent is not in list of favourite tutors of parent"
                    return Response(return_info)

                try:
                    tutor_ob = Tutor.objects.get(id=fav_tutor)
                except:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Could not find favorite tutor"
                    return Response(return_info)

                try:
                    sub_ob = Subject.objects.get(id=subject)
                except:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Could not find subject"
                    return Response(return_info)

                subject_list = []
                t_subs = TutorSubject.objects.filter(tutor=fav_tutor)
                for t_sub in t_subs:
                    subject_list.append(t_sub.subject)

                if sub_ob not in subject_list or t_subs.count() == 0:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Cannot make a request to a tutor who does not teach the subject " + sub_ob.subject_field
                    return Response(return_info)

            for r in made_requests_serializer.data:
                made_requests_count += 1
                total_made_requests_cost += r['time']

            if (made_requests_count + len(available_days)) > 10:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Cannot have more than 10 requests pending at a given time"
                return Response(return_info)

            if len(available_days) <= 0:
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Cannot have no available days for a request"
                return Response(return_info)

            timezone.activate(pytz.timezone("Asia/Manila"))

            for day in available_days:
                start = day['start_date_time'][:-1]
                start = start + "+0800"
                end = day['end_date_time'][:-1]
                end = end + "+0800"
                start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f%z")
                end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%f%z")
                if (((end-start).seconds / 3600) < int(time)):
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Available time " + day['start_date_time'] + " and " + day['end_date_time'] + " is shorter than " + str(time) + " hours"
                    return Response(return_info)
                if end < start:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: End Date  " + day['end_date_time'] + " is earlier that start date " +  day['start_date_time']
                    return Response(return_info)

                for r in made_requests_serializer.data:
                    av_days_of_r = AvailableDays.objects.filter(request=r['id'])

                    for av_day in av_days_of_r:
                        if (timezone.localtime(av_day.start_date_time) <= start < timezone.localtime(av_day.end_date_time)) or (timezone.localtime(av_day.start_date_time) < end <= timezone.localtime(av_day.end_date_time)):
                            return_info['return_status'] = "error"
                            return_info['return_message'] = "Error: Already have a request under the same available day and time"
                            return Response(return_info)

                for r in accepted_requests_serializer.data:
                    av_days_of_r = AvailableDays.objects.filter(request=r['id'])

                    for av_day in av_days_of_r:
                        if (timezone.localtime(av_day.start_date_time) <= start < timezone.localtime(av_day.end_date_time)) or (timezone.localtime(av_day.start_date_time) < end <= timezone.localtime(av_day.end_date_time)):
                            return_info['return_status'] = "error"
                            return_info['return_message'] = "Error: Already have a request under the same available day and time"
                            return Response(return_info)

            #else:
            #check if parent has enough credits to make the request
            if ((total_made_requests_cost + (time * len(available_days))) > parent_credits):
                return_info['return_status'] = "error"
                return_info['return_message'] = "Error: Not enough credits in account to make request"
                return Response(return_info)

            #make the request object
            #create available_days objects

            available_days_return = []
            return_info['request'] = []

            for day in available_days:
                data = {
                    "parent": parent.id,
                    "child": child.id,
                    "extra_files": extra_files,
                    "status": 'pending',
                    "is_favourite": is_favourite,
                    "subject": subject,
                    "topics": topics,
                    "special_request": special_request,
                    "fav_tutor": fav_tutor,
                    "time": time,
                    "declined_tutors": [],
                    "declined_reason": ""
                }

                request_serializer_class = RequestsSerializer(data=data)
                if request_serializer_class.is_valid():
                    request_serializer_class.save()
                    return_info['request'].append(request_serializer_class.data)
                else:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = displayErrors(request_serializer_class.errors)
                    return Response(return_info)

                start = day['start_date_time'][:-1]
                start = start + "+0800"
                end = day['end_date_time'][:-1]
                end = end + "+0800"
                data = {
                    "request": request_serializer_class.data['id'],
                    "start_date_time": start,
                    "end_date_time": end
                }

                serializer_class = AvailableDaysSerializer(data=data)
                if serializer_class.is_valid():
                    serializer_class.save()
                    available_days_return.append(serializer_class.data)
                else:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = displayErrors(serializer_class.errors)
                    return Response(return_info)

            return_info['available_days'] = available_days_return

            return_info['return_status'] = "success"
            return_info['return_message'] = "Request/s were made successfully"
            parent.first_use = True
            parent.save()
            sendBroadcast('%s made a request!' % parent.email)
            return Response(return_info)
        except Exception as e:
            return_info = {}
            return_info['return_status'] = "error"
            return_info['return_message'] = str(e)
            return Response(return_info)


class TutorAcceptRequest(APIView):
    """
    POST:
    Description: Tutor accepts request
    input:
    {
        "request_id": id of request,
        "available_day_id": id of available day,
        "tutor_id": id of tutor,
        "start_date_time": Datetime (the start time of the tutoring session - legacy)
    }
    output:
    {
        "return_status": string,
        "return_status": string,
        "request":{
            "parent": id of parent,
            "child": id of child,
            "tutor_email": string,
            "time": Datetime,
            "extra_files": string,
            "status": string,
            "is_favourite": String,
            "subject": id of subject,
            "topics": String,
            "special_request": String
        }
        "parent": {
            "username": string,
            "first_name": string,
            "last_name": string,
            "email": string,
            "credits": float,
            "status": boolean,
            "phone": string,
            "picture": string
        }
        "session{
            "request": id of request,
            "tutor": id of tutor
            "zoom_link": string,
            "active": string
            "start_date_time": Datetime,
            "end_date_time": Datetime,
        }
        "conversation":{
            "session": id of session
        }

    }
    """
    def post(self, request, format=None):
        updated_elements= {}
        updated_elements['return_status'] = ""
        updated_elements['return_message'] = ""

        request_id = request.data['request_id']
        available_day_id = request.data['available_day_id']
        tutor_id = request.data['tutor_id']

        pending_request = Requests.objects.get(id=request_id)
        available_day = AvailableDays.objects.get(id=available_day_id)

        start_date_time = request.data['start_date_time']

        # start_time = start_date_time.split('T')[0]
        # start_year = int(start_time.split('-')[0])
        # start_month = int(start_time.split('-')[1])
        # start_day = int(start_time.split('-')[2])
        #
        # # start_time
        # start_time = start_date_time[:-1]
        # start_time = start_time + "+0800"
        # # start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%f%z")
        # start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        # end_time = start_time + datetime.timedelta(hours=int(pending_request.time))

        # if not ((start_time >= available_day.start_date_time and start_time < available_day.end_date_time) and (end_time <= available_day.end_date_time and end_time > available_day.start_date_time)):
        #     updated_elements['return_status'] = "error"
        #     updated_elements['return_message'] = "Error: Time chosen doesnt not full under the bound of available date and time"
        #     return Response(updated_elements)

        if available_day.request.id != pending_request.id:
            updated_elements['return_status'] = "error"
            updated_elements['return_message'] = "Error: Available day does not match with the given request"
            return Response(updated_elements)

        if pending_request.status != 'pending':
            updated_elements['return_status'] = "error"
            updated_elements['return_message'] = "Error: Request is not pending"
            return Response(updated_elements)

        sess_obs = Session.objects.filter(request=request_id)
        if sess_obs.count() > 0:
            updated_elements['return_status'] = "error"
            updated_elements['return_message'] = "Error: Request has already been accepted"
            return Response(updated_elements)

        tutor = Tutor.objects.get(id=tutor_id)

        parent_id = pending_request.parent.id

        parent = Parent.objects.get(id=parent_id)

        #check if request interferes with accepted schedule
        tutor_sessions = Session.objects.filter(tutor=tutor.id, active="True")
        tutor_sessions_serializer = SessionSerializer(tutor_sessions, many=True)

        timezone.activate(pytz.timezone("Asia/Manila"))

        for s in tutor_sessions:
            if(timezone.localtime(s.start_date_time) <= timezone.localtime(available_day.start_date_time) < timezone.localtime(s.end_date_time) or timezone.localtime(s.start_date_time) < timezone.localtime(available_day.end_date_time) <= timezone.localtime(s.end_date_time)):
                updated_elements['return_status'] = "error"
                updated_elements['return_message'] = "Error: Request being made has time conflicts with previous requests and upcoming sessions"
                return Response(updated_elements)

        if parent.credits >= pending_request.time:
            # Create zoom meeting info
            tutee = pending_request.child.first_name + " " + pending_request.child.last_name
            sub_ob = Subject.objects.get(id=pending_request.subject.id)
            subject = sub_ob.subject_field
            start_time = available_day.start_date_time.date().strftime("%Y-%m-%dT%H:%M:%S")
            duration = str(pending_request.time * 60)
            # res = zoom_create_meeting(tutee, subject, start_time, duration)
            
            # Create jitsi meeting info
            # meet_suffix = tutee.replace(' ', '') + subject + str(random.randint(1000, 9999))
            # meet_link = os.environ['MEET_URL') + meet_suffix 
            # print(meet_link)

            TUTOR_TYPE = 1
            STUDENT_TYPE = 2

            ONE_ROOM = 0
            MULTI_ROOM = 4

            # Create agora meeting info
            room_name = f'{subject} with Tutor {tutor.first_name}'
            tutor_join_link = os.environ['AGORA_URL'] + f'get_agora?account={tutor.first_name}&room={room_name}&roleType={TUTOR_TYPE}&roomType={ONE_ROOM}&minutes={(pending_request.time * 60) + 10}'
            tutee_join_link = os.environ['AGORA_URL'] + f'get_agora?account={pending_request.child.first_name}&room={room_name}&roleType={STUDENT_TYPE}&roomType={ONE_ROOM}&minutes={(pending_request.time * 60) + 10}'
            print(tutor_join_link)
            print(tutee_join_link)

            session_data = {
                "request": pending_request.id,
                'tutor_join_link': tutor_join_link,
                'tutee_join_link': tutee_join_link,
                "active": "True",
                "start_date_time": available_day.start_date_time,
                "end_date_time": available_day.end_date_time,
                "tutor": tutor_id
            }

            pending_request.status = "accepted"
            print('accepted')
            pending_request.tutor = tutor.id
            pending_request.save()
            print('request saved')

            parent.credits -= pending_request.time
            parent.save()
            print('parent saved')

            pending_request_serializer = RequestsSerializer(pending_request)
            parent_serializer = ParentSerializer(parent)
            updated_elements["request"] = pending_request_serializer.data
            updated_elements["parent"] = parent_serializer.data
            print('serializers')

            session_serializer = SessionSerializer(data=session_data)
            print('session serializer made')
            print(session_serializer.is_valid())
            if session_serializer.is_valid():
                print('saving...')
                session_serializer.save()
                print('saved')

                updated_elements["session"] = session_serializer.data

                conversation_data = {
                    "session": session_serializer.data['id'],
                    "parent": parent.id,
                    "tutor": tutor.id,
                    "active": True
                }

                conversation_serializer = ConversationSerializer(data=conversation_data)
                if conversation_serializer.is_valid():
                    conversation_serializer.save()

                    updated_elements["conversation"] = conversation_serializer.data
                    updated_elements['return_status'] = "success"
                    updated_elements['return_message'] = "Request successfully accepted"

                    convo = Conversation.objects.get(session=session_serializer.data['id'])

                    timezone.activate(pytz.timezone("Asia/Manila"))
                    data = {
                        "conversation": convo.id,
                    	"sender":"tutor",
                    	"text": "Hello! My name is " + tutor.first_name + " and I will be teaching " + pending_request.child.first_name + " in " + pending_request.subject.subject_field + ". If you need to send any additional files, kindly upload them in "+ pending_request.extra_files + ". If you have any questions, don't hesitate to ask me!",
                    	"time_sent": timezone.localtime(timezone.now()),
                    	"parent_seen": False,
                        "tutor_seen": False
                    }

                    msg_serializer = MessageSerializer(data=data)
                    if msg_serializer.is_valid():
                        msg_serializer.save()
                        return Response(updated_elements)
                    else:
                        return Response(conversation_serializer.errors)

                return Response(conversation_serializer.errors)

            return Response(session_serializer.errors)

        updated_elements['return_status'] = "error"
        updated_elements['return_message'] = "Error: Parent does not have enough credits"
        return Response(updated_elements)

class AllParentTransactions(APIView):
    """
    POST:
    Description: Get All transactions of a certain parent via parent id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "parent": id of parent,
        "credits": float,
        "amount": float,
        "method": string
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        queryset = PayMongoTransaction.objects.filter(parent=parent_id)
        serializer_class = PayMongoTransactionSerializer(queryset, many=True)

        return Response(serializer_class.data)

class MakeTutorApplication(APIView):
    """
    POST:
    Description: make a tutor application
    Input:
    {
        "first_name" = String,
        "last_name" = String,
        "sex" = String,
        "email" = String,
        "subjects" = String,
        "tutoring_experience" = String,
        "grade_levels" = String,
        "identification_photo" = String,
        "TOR" = String
    }
    Output:
    {
        "tutor_application":
        {
            "first_name" = String,
            "last_name" = String,
            "sex" = String,
            "email" = String,
            "subjects" = String,
            "tutoring_experience" = String,
            "grade_levels" = String,
            "identification_photo" = String,
            "TOR" = String
        }
    }
    """
    def post(self, request, format=None):
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        sex = request.data['sex']
        email = request.data['email']
        subjects = request.data['subjects']
        tutoring_experience = request.data['tutoring_experience']
        grade_levels = request.data['grade_levels']
        identification_photo = request.data['identification_photo']
        TOR = request.data['TOR']

        #make the tutor application object
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "sex": sex,
            "email": email,
            "subjects": subjects,
            "tutoring_experience": tutoring_experience,
            "grade_levels": grade_levels,
            "identification_photo": identification_photo,
            "TOR": TOR
        }

        tutor_application_serializer_class = TutorApplicationSerializer(data=data)
        if tutor_application_serializer_class.is_valid():
            tutor_application_serializer_class.save()
            return_info = {}
            return_info['tutor_application'] = tutor_application_serializer_class.data

            return Response(tutor_application_serializer_class.data)
        else:
            return Response(tutor_application_serializer_class.errors)


class AddChild(APIView):
    """
    POST:
    Description: Add children to parent
    Input:
    {
        children : [
            {
            	"email": String,
            	"first_name": String,
            	"last_name": String,
            	"age" : Integer,
            	"year_level": String,
            	"school": String
            }
        ],
        "parent" : ID of parent object
    }
    Output:
    {
        "child": Child Object
        "return_status": string (Error or Success),
        "return_message": string (Message about return status)
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['children'] = []
        children = request.data['children']
        parent_id = request.data['parent']
        # email = request.data['email']
        # first_name = request.data['first_name']
        # last_name = request.data['last_name']
        # age = request.data['age']
        # year_level = request.data['year_level']
        # school = request.data['school']

        try:
            parent = Parent.objects.get(id=parent_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent not found"
            return Response(return_info)

        for child in children:
            try:
                child['age'] = int(child['age'])
            except Exception as e:
                child['age'] = None
            data = {
                "parent" : parent_id,
            	"email": child['email'],
            	"first_name": child['first_name'],
            	"last_name": child['last_name'],
            	"age" : child['age'],
            	"year_level": child['year_level'],
            	"school": child['school']
            }

            child_serializer = ChildSerializer(data=data)
            if child_serializer.is_valid():
                child_serializer.save()
                return_info['children'].append(child_serializer.data)

            else:
                return_info['return_status'] = "error"
                return_info['return_message'] = child_serializer.errors
                return Response(return_info)

        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully created child/children"
        return Response(return_info)
