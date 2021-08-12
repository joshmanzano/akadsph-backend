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
from core.views import zoom_create_meeting
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
    TutorStrikeSerializer,
    CreditTrackerSerializer
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
    TutorStrike,
    CreditTracker
    )

class AddCreditToParent(APIView):
    """
    POST:
    Description: Add 1-10 credits to a parents account
    Input:
    {
        "parent_id": id of parent
        "credits": int (number of credits to be added)
    }
    Output:
    {
        "return_status": String (error or success)
        "return_message": String (Message describing the return_status)
    }
    """
    def post(self, request, format=None):
        return_info = {}
        parent_id = request.data['parent_id']
        credits = request.data['credits']

        try:
            parent_ob = Parent.objects.get(id=parent_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent not found"
            return Response(return_info)

        try:
            credits = int(credits)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: credits not of integer type"
            return Response(return_info)

        if credits > 10 or credits < 1:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Invalid credit amount. can only add 1-10 credits."
            return Response(return_info)

        parent_ob.credits = parent_ob.credits + credits
        parent_ob.save()

        timezone.activate(pytz.timezone("Asia/Manila"))
        now = timezone.localtime(timezone.now())

        CreditTracker(parent=parent_ob, time=now, add_credit=credits, subtract_credit=0).save()

        return_info['return_status'] = "success"
        credit = str(credits)
        return_info['return_message'] = "Successfully added " + credit + " credit/s to Parent with id " + str(parent_id) + "."
        return Response(return_info)


class SubtractCreditToParent(APIView):
    """
    POST:
    Description: Subtract 1-10 credits to a parents account
    Input:
    {
        "parent_id": id of parent
        "credits": int (number of credits to be subtracted)
    }
    Output:
    {
        "return_status": String (error or success)
        "return_message": String (Message describing the return_status)
    }
    """
    def post(self, request, format=None):
        return_info = {}
        parent_id = request.data['parent_id']
        credits = request.data['credits']

        try:
            parent_ob = Parent.objects.get(id=parent_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent not found"
            return Response(return_info)

        try:
            credits = int(credits)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: credits not of integer type"
            return Response(return_info)

        if credits > 10 or credits < 1:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Invalid credit amount. Can only subtract 1-10 credits."
            return Response(return_info)

        amount = parent_ob.credits - credits

        if amount < 0:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Invalid credit amount. Amount of credits will give Parent negative credits."
            return Response(return_info)

        parent_ob.credits = parent_ob.credits - credits
        parent_ob.save()

        timezone.activate(pytz.timezone("Asia/Manila"))
        now = timezone.localtime(timezone.now())

        CreditTracker(parent=parent_ob, time=now, add_credit=0, subtract_credit=credits).save()

        return_info['return_status'] = "success"
        credit = str(credits)
        return_info['return_message'] = "Successfully subtracted " + credit + " credit/s to Parent with id " + str(parent_id) + "."
        return Response(return_info)
