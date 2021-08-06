from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import ParentNotification, TutorNotification
from core.serializers import ParentNotificationSerializer, TutorNotificationSerializer
from django.core.exceptions import ObjectDoesNotExist
import requests
import json

class GetTutorNotifications(APIView):
    """
    POST
    Description: Gives 10 most recent notifications of a certain tutor given a tutor id
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "notifications": [
            {
                "tutor": id of tutor,
                "is_seen": Boolean,
                "notification": string,
                "time": datetime of when notification was created
            },
        ]
    }
    """
    def post(self, request, format=None):
        tutor_id = request.data['tutor_id']
        res_data = {}

        notifications = TutorNotification.objects.filter(tutor=tutor_id).order_by('-time')[:25]
        serializer_class = TutorNotificationSerializer(notifications, many=True)

        res_data['notifications'] = serializer_class.data
        return Response(res_data)

class GetParentNotifications(APIView):
    """
    POST
    Description: Gives 10 most recent notifications of a certain parent given a tutor id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "notifications": [
            {
                "parent": id of parent,
                "is_seen": Boolean,
                "notification": string,
                "time": datetime of when notification was created
            },
        ]
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        res_data = {}

        notifications = ParentNotification.objects.filter(parent=parent_id).order_by('-time')[:25]
        serializer_class = ParentNotificationSerializer(notifications, many=True)

        res_data['notifications'] = serializer_class.data
        return Response(serializer_class.data)

class SeenAllTutorNotifications(APIView):
    """
    POST
    Description: Makes all unseen notifications of a tutor seen
    input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "notifications": [
            {
                "tutor": id of tutor,
                "is_seen": Boolean,
                "notification": string,
                "time": datetime of when notification was created
            },
        ]
    }
    """
    def post(self, request, format=None):
        tutor_id = request.data['tutor_id']
        res_data = {}
        res_data['notifications'] = []

        queryset = TutorNotification.objects.filter(tutor=tutor_id, is_seen=False)
        for notif in queryset:
            notif.is_seen = True
            notif.save()

            serializer_class = TutorNotificationSerializer(notif)
            res_data['notifications'].append(serializer_class.data)

        return Response(res_data)

class SeenAllParentNotifications(APIView):
    """
    POST
    Description: Makes all unseen notifications of a parent seen
    input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "notifications": [
            {
                "parent": id of parent,
                "is_seen": Boolean,
                "notification": string,
                "time": datetime of when notification was created
            },
        ]
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        res_data = {}
        res_data['notifications'] = []

        queryset = ParentNotification.objects.filter(parent=parent_id, is_seen=False)
        for notif in queryset:
            notif.is_seen = True
            notif.save()

            serializer_class = ParentNotificationSerializer(notif)
            res_data['notifications'].append(serializer_class.data)

        return Response(res_data)
