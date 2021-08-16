from rest_framework import permissions
from rest_framework.views import APIView
import requests
import json
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import datetime
from core.extra_functions import getStartDateAndEndDateOfWeek
import pytz
from core.ws import sendUpdate, sendBroadcast
from core.send_email import SendEmail

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
    AvailableDaysSerializer,
    SubjectSerializer,
    AdminSettingSerializer,
    ParentSettingSerializer,
    TutorSettingSerializer,
    ParentNotificationSerializer,
    TutorNotificationSerializer,
    TutorSubjectSerializer,
    TutorPayoutSerializer,
    TutorStrikeSerializer
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
    AvailableDays,
    Subject,
    AdminSetting,
    ParentSetting,
    TutorSetting,
    ParentNotification,
    TutorNotification,
    TutorSubject,
    TutorPayout,
    TutorStrike
    )

class FindAvailableDaysRequest(APIView):
    """
    POST:
    Description: Find the available days attached to a specific request
    Input:
    {
    "request_id": id of request
    }
    Output:
    {
        "request": id of request,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
    }
    """
    def post(self, request, format=None):
        request_id = request.data['request_id']

        queryset = AvailableDays.objects.filter(request=request_id)
        serializer_class = AvailableDaysSerializer(queryset, many=True)

        return Response(serializer_class.data)

class SpecificRequest(APIView):
    """
    POST:
    Description: Find specific request by request_id
    Input:
    {
        "request_id": id of request
    }
    Output:
    {
        "request": {
            request object
        }
    }
    """

    def post(self, request, format=None):
        request_id = request.data['request_id']
        return_info = {}

        queryset = Requests.objects.get(id=request_id)
        serializer_class = RequestsSerializer(queryset)
        return_info['request'] = serializer_class.data
        return Response(return_info)

class ExtendSession(APIView):
    """
    POST:
    Description: Extend a session
    Input:
    {
        "session_id": id of session you want to extend
        "duration": integer (how long the session will be)
    }
    Output:
    {
        "request": request object,
        "available_day": available day objecy
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info["session"] = None
        session_id = request.data['session_id']
        duration = int(request.data['duration'])

        try:
            duration = int(request.data['duration'])
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Duration is not INT type"
            return Response(return_info)

        try:
            sess_ob = Session.objects.get(id=session_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Session not found"
            return Response(return_info)

        parent_ob = Parent.objects.get(id=sess_ob.request.parent.id)

        if parent_ob.credits < duration:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: You does not have enough credits to extend the session"
            return Response(return_info)

        request_data = {
            "parent": parent_ob.id,
            "child": sess_ob.request.child.id,
            "extra_files": sess_ob.request.extra_files,
            "status": 'pending',
            "is_favourite": True,
            "subject": sess_ob.request.subject,
            "topics": sess_ob.request.topics,
            "special_request": sess_ob.request.special_request,
            "fav_tutor": sess_ob.tutor.id,
            "time": duration,
            "declined_tutors": [],
            "declined_reason": ""
        }

        request_serializer_class = RequestsSerializer(data=request_data)
        if request_serializer_class.is_valid():
            request_serializer_class.save()
            return_info['request'] = request_serializer_class.data
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = displayErrors(request_serializer_class.errors)
            return Response(return_info)

        start = sess_ob.end_date_time
        end = sess_ob.end_date_time + datetime.timedelta(hours=duration)
        data = {
            "request": request_serializer_class.data['id'],
            "start_date_time": start,
            "end_date_time": end
        }

        serializer_class = AvailableDaysSerializer(data=data)
        if serializer_class.is_valid():
            serializer_class.save()
            return_info['available_days'] = serializer_class.data
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = displayErrors(serializer_class.errors)
            return Response(return_info)

        sendUpdate('parent', 'update', parent_ob.id)
        sendUpdate('tutor', 'update', sess_ob.tutor.id)
        sendBroadcast("Parent " + parent_ob.first_name + " sent an extension request to " + sess_ob.tutor.first_name)

        return Response(return_info)
        # Create zoom meeting info
        # tutee = sess_ob.request.child.first_name + " " + sess_ob.request.child.last_name
        # sub_ob = Subject.objects.get(id=sess_ob.request.subject.id)
        # subject = sub_ob.subject_field
        # start_time = sess_ob.end_date_time.date().strftime("%Y-%m-%dT%H:%M:%S")
        # end_time = sess_ob.end_date_time + datetime.timedelta(hours=duration)
        # meeting_duration = str(duration * 60)
        # res = zoom_create_meeting(tutee, subject, start_time, meeting_duration)
        #
        # session_data = {
        #     "request": sess_ob.request.id,
        # 	"start_zoom_link": res['start_url'],
        #     "join_zoom_link": res['join_url'],
        #     "zoom_id": res['zoom_id'],
        # 	"active": sess_ob.active,
        # 	"start_date_time": sess_ob.end_date_time,
        # 	"end_date_time": end_time,
        # 	"tutor": sess_ob.tutor.id
        # }
        #
        # session_serializer = SessionSerializer(data=session_data)
        # if session_serializer.is_valid():
        #     session_serializer.save()
        #     parent_ob.credits -= duration
        #     parent_ob.save()
        #     return_info["session"] = session_serializer.data
        #     return_info['return_status'] = "success"
        #     return_info['return_message'] = "Successfully created a new session for extension"
        #     return Response(return_info)
        # else:
        #     return Response(session_serializer.errors)

class CancelSession(APIView):
    """
    POST:
    Description: Cancel a session that is at least 24 hours away
    Input:
    {
        "parent_id": id of parent,
        "session_id": id of session
        "reason": reason,
    }
    Output:
    {
        "return_status": string,
        "return_message": string,
        "session": updated session object
        "request": updated request object
    }
    """
    def post(self, request, format=None):
        session_id = request.data['session_id']
        parent_id = request.data['parent_id']
        reason = request.data['reason']
        return_info = {}
        return_info['return_status'] = ""
        return_info['return_message'] = ""

        try:
            session = Session.objects.get(id=session_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Session not found"
            return Response(return_info)

        request_id = session.request.id
        request_ob = Requests.objects.get(id=request_id)

        start_date_time = session.start_date_time
        timezone.activate(pytz.timezone("Asia/Manila"))
        now = timezone.localtime(timezone.now())

        #check if session has already been cancelled
        if request_ob.status == 'cancelled':
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: session has already been cancelled"
            return Response(return_info)
        elif request_ob.status == 'finished':
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Cannot cancel a session that has already ended"
            return Response(return_info)
        #if 24 hours before the session
        elif now < (start_date_time - datetime.timedelta(hours=24)):

            session.active = 'False'
            session.save()

            request_ob.status = 'cancelled'
            request_ob.save()

            session_serializer = SessionSerializer(session)
            request_serializer = RequestsSerializer(request_ob)

            #Refund the hours
            parent_ob = Parent.objects.get(id=request_ob.parent.id)
            parent_ob.credits = parent_ob.credits + request_ob.time
            parent_ob.save()

            message = parent_ob.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " \nbecause of the following reason: " + reason + ". "
            message2 = parent_ob.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " because of the following reason: " + reason + ". "
            TutorNotification(tutor=session.tutor, is_seen=False, notification=message2).save()
            sub = "Cancellation of Session"
            SendEmail(sub, message, session.tutor.email)
            sendUpdate('parent', 'update', parent_ob.id)
            sendUpdate('tutor', 'update', session.tutor.id)
            sendBroadcast(message2)
            #TODO: ADD SMS

            return_info['session'] = session_serializer.data
            return_info['request'] = request_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully cancelled the upcoming session"

            return Response(return_info)
        elif (now < start_date_time) and (now > (start_date_time - datetime.timedelta(hours=24))):
            session.active = 'False'
            session.save()

            request_ob.status = 'cancelled'
            request_ob.save()

            session_serializer = SessionSerializer(session)
            request_serializer = RequestsSerializer(request_ob)

            parent_ob = Parent.objects.get(id=request_ob.parent.id)

            message = parent_ob.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " \nbecause of the following reason: \n" + reason + ". "
            message2 = parent_ob.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " because of the following reason: " + reason + ". "
            TutorNotification(tutor=session.tutor, is_seen=False, notification=message2).save()
            sub = "Cancellation of Session"
            SendEmail(sub, message, session.tutor.email)
            sendUpdate('parent', 'update', parent_ob.id)
            sendUpdate('tutor', 'update', session.tutor.id)
            sendBroadcast(message2)
            #TODO: ADD SMS

            return_info['session'] = session_serializer.data
            return_info['request'] = request_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully cancelled the upcoming session"

            return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Unkown Error Occured"
            return Response(return_info)

class TutorCancelSession(APIView):
    """
    POST:
    Description: Cancel a session that is at least 24 hours away
    Input:
    {
        "tutor_id": id of tutor,
        "session_id": id of session,
        "reason": string
    }
    Output:
    {
        "return_status": string,
        "return_message": string,
        "session": updated session object
        "request": updated request object
    }
    """
    def post(self, request, format=None):
        session_id = request.data['session_id']
        tutor_id = request.data['tutor_id']
        reason = request.data['reason']
        return_info = {}
        return_info['return_status'] = ""
        return_info['return_message'] = ""

        try:
            session = Session.objects.get(id=session_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Session not found"
            return Response(return_info)

        tutor = Tutor.objects.get(id=tutor_id)

        request_id = session.request.id
        request_ob = Requests.objects.get(id=request_id)

        start_date_time = session.start_date_time
        timezone.activate(pytz.timezone("Asia/Manila"))
        now = timezone.localtime(timezone.now())

        #check if session has already been cancelled
        if request_ob.status == 'cancelled':
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: session has already been cancelled"
            return Response(return_info)
        elif request_ob.status == 'finished':
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Cannot cancel a session that has already ended"
            return Response(return_info)
        #if 24 hours before the session
        elif now < (start_date_time - datetime.timedelta(hours=24)):

            session.active = 'False'
            session.save()

            request_ob.status = 'cancelled'
            request_ob.save()

            session_serializer = SessionSerializer(session)
            request_serializer = RequestsSerializer(request_ob)

            #Refund the hours
            parent_ob = Parent.objects.get(id=request_ob.parent.id)
            parent_ob.credits = parent_ob.credits + request_ob.time
            parent_ob.save()

            message = tutor.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " \nbecause of the following reason: " + reason + ". \n\n" + str(request_ob.time) + " credit(s) have been refunded to your account"
            message2 = tutor.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " because of the following reason: " + reason + ". " + str(request_ob.time) + " credit(s) have been refunded to your account"
            ParentNotification(parent=parent_ob, is_seen=False, notification=message2).save()
            sub = "Cancellation of Session"
            SendEmail(sub, message, parent_ob.email)
            sendUpdate('parent', 'update', parent_ob.id)
            sendUpdate('tutor', 'update', tutor.id)
            sendBroadcast(message2)
            #TODO: ADD SMS

            return_info['session'] = session_serializer.data
            return_info['request'] = request_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully cancelled the upcoming session"

            return Response(return_info)
        elif (now < start_date_time) and (now > (start_date_time - datetime.timedelta(hours=24))):
            session.active = 'False'
            session.save()

            request_ob.status = 'cancelled'
            request_ob.save()

            session_serializer = SessionSerializer(session)
            request_serializer = RequestsSerializer(request_ob)

            #Refund the hours
            parent_ob = Parent.objects.get(id=request_ob.parent.id)
            parent_ob.credits = parent_ob.credits + request_ob.time
            parent_ob.save()

            TutorStrike(tutor=tutor, time=now, reason='Cancelled a Sessionon the day and time ' + str(timezone.localtime(session.start_date_time)) + ' within 24 Hours', session=session).save()
            message = tutor.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " \nbecause of the following reason: " + reason + ". \n\n" + str(request_ob.time) + " credit(s) have been refunded to your account"
            message2 = tutor.first_name + " has cancelled the session on the day and time " + str(timezone.localtime(session.start_date_time)) + " because of the following reason: " + reason + ". " + str(request_ob.time) + " credit(s) have been refunded to your account"
            ParentNotification(parent=parent_ob, is_seen=False, notification=message2).save()
            sub = "Cancellation of Session"
            SendEmail(sub, message, parent_ob.email)
            sendUpdate('parent', 'update', parent_ob.id)
            sendUpdate('tutor', 'update', tutor.id)
            sendBroadcast(message2)
            #TODO: ADD SMS

            return_info['session'] = session_serializer.data
            return_info['request'] = request_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully cancelled the upcoming session"

            return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Unkown Error Occured"
            return Response(return_info)

class EndSession(APIView):
    """
    POST:
    Description: Set the 'active' field of session to False and 'status' field of request to 'finished' and add to tutorpayout
    Input:
    {
        "session_id": id of session
    }
    Output:
    {
        "session": updated session object
        "request": updated request object
    }
    """

    def post(self, request, format=None):
        session_id = request.data['session_id']

        session = Session.objects.get(id=session_id)

        if session.active == 'True':
            session.active = 'False'

            request_id = session.request.id
            request_ob = Requests.objects.get(id=request_id)

            request_ob.status = 'finished'

            session.save()
            request_ob.save()

            session_serializer = SessionSerializer(session)
            request_serializer = RequestsSerializer(request_ob)

            updated_elements = {}

            updated_elements['session'] = session_serializer.data
            updated_elements['request'] = request_serializer.data

            week_bracket = getStartDateAndEndDateOfWeek(str(session.end_date_time))

            # tutor_payout = None

            tutor_payout = TutorPayout.objects.filter(tutor=session.tutor.id).filter(week_bracket=week_bracket)

            if tutor_payout.count() == 1:
                tutor_payout[0].session.add(session)
                tutor_payout[0].save()

            elif tutor_payout.count() == 0:
                session_list = []
                session_list.append(session.id)

                tutor_payout_data = {
                    "photo": "temp data",
                    "week_bracket": week_bracket,
                    "session": session_list,
                    "tutor": session.tutor.id,
                    "isPaid": False
                }

                tutor_payout_serializer_class = TutorPayoutSerializer(data=tutor_payout_data)
                if tutor_payout_serializer_class.is_valid():
                    tutor_payout_serializer_class.save()
                    updated_elements['tutor_payout'] = tutor_payout_serializer_class.data
                else:
                    return Response(tutor_payout_serializer_class.errors)

            return Response(updated_elements)
        else:
            return Response('Session already finished')

class TutorDeclineRequest(APIView):
    """
    POST:
    Description: Cancel a request given a request id
    Input:
    {
        "request": id of request,
        "tutor": id of tutor who cancelled
        "decline_reason": "" (optional- only put input here if a favorite tutor declines)
    }
    Output:
    {
        "return_status": string,
        "return_message": string,
        "request": {
            request object
        }
    }
    """
    def post(self, request, format=None):
        request_id = request.data['request']
        tutor_id = request.data['tutor']
        decline_reason = request.data['decline_reason']
        queryset = Requests.objects.get(id=request_id)
        return_info = {}
        return_info['return_status'] = ""
        return_info['return_message'] = ""

        if (queryset.status == 'pending'):
            # CASE 1: A favourite tutor who is supposed to be in the fav_tutor field declines
            if queryset.is_favourite == True and queryset.fav_tutor != None:
                if tutor_id == queryset.fav_tutor.id:
                    queryset.declined_tutors.add(Tutor.objects.get(id=tutor_id))
                    queryset.declined_reason = decline_reason
                    queryset.save()
                    request_serializer = RequestsSerializer(queryset)

                    return_info['return_status'] = "success"
                    return_info['return_message'] = "Successfully declined the pending request"
                    return_info['request'] = request_serializer.data
                    return Response(return_info)
                else:
                    return_info['return_status'] = "error"
                    return_info['return_message'] = "Error: Request does not having a matching tutor id with yours"
                    return Response(return_info)
            # CASE 2: The set of Favourite tutors of a certain parent are declining the request
            elif queryset.is_favourite == True and queryset.fav_tutor == None:
                tutor_ob = Tutor.objects.get(id=tutor_id)
                fav_list = FavouriteTutor.objects.filter(parent=queryset.parent.id, tutor=tutor_id)
                for fav in fav_list:
                    if tutor_id == fav.tutor.id:
                        queryset.declined_tutors.add(Tutor.objects.get(id=tutor_id))
                        queryset.declined_reason = decline_reason
                        queryset.save()
                        request_serializer = RequestsSerializer(queryset)

                        return_info['return_status'] = "success"
                        return_info['return_message'] = "Successfully declined the pending request"
                        return_info['request'] = request_serializer.data
                        return Response(return_info)
                    else:
                        return_info['return_status'] = "error"
                        return_info['return_message'] = "Error: Tutor id not found in favourite tutor list"
                        return Response(return_info)
            #CASE 3: A tutor is declining a non-favourited request
            else:
                tutor_ob = Tutor.objects.get(id=tutor_id)
                queryset.declined_tutors.add(Tutor.objects.get(id=tutor_id))
                queryset.save()
                return_info['return_status'] = "success"
                return_info['return_message'] = "Successfully declined the pending request"
                return_info['request'] = queryset.data
                return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Request being declined is not pending"
            return Response(return_info)

class ParentCancelRequest(APIView):
    """
    POST:
    Description: a Parent will Cancel a request given a request id
    Input:
    {
        "request": id of request
    }
    Output:
    {
        "return_status": string,
        "return_message": string,
        "request": {
            request object
        }
    }
    """
    def post(self, request, format=None):
        request_id = request.data['request']
        queryset = Requests.objects.get(id=request_id)
        return_info = {}
        return_info['return_status'] = ""
        return_info['return_message'] = ""

        if (queryset.status == 'pending'):
            queryset.status = 'cancelled'
            queryset.save()
            request_serializer = RequestsSerializer(queryset)

            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully cancelled the pending request"
            return_info['request'] = request_serializer.data
            return Response(return_info)

        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Request being cancelled is not pending"
            return Response(return_info)
