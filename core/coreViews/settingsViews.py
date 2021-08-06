from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import ParentSetting, TutorSetting
from core.serializers import ParentSettingSerializer, TutorSettingSerializer
from django.core.exceptions import ObjectDoesNotExist
import requests
import json

class UpdateParentSettings(APIView):
    """
    POST:
    Description: Updates the parent settings
    Input:
    {
    "parent_id": id of parent,
    "settings": [
            {
                "field_name": string,
                "value": string
            }
        ...
        ]
    }
    Output:
    {
    "parent_id": id of parent,
    "settings": [
            {
                "field_name": string,
                "value": string
            }
        ...
        ]
    }
    """
    def post(self, request, format=None):
        parent_id = request.data['parent_id']
        settings = request.data['settings']
        res_data = {}
        res_data['parent_id'] = parent_id
        res_data['settings'] = []

        for item in settings:
            queryset = ParentSetting.objects.filter(parent=parent_id, field_name=item['field_name'])
            count = queryset.count()
            setting_value = {}

            if count == 0:
                data = {
                "parent": parent_id,
                "field_name": item['field_name'],
                "value": item['value']
                }

                serializer_class = ParentSettingSerializer(data=data)
                if serializer_class.is_valid():
                    serializer_class.save()

                    setting_value['field_name'] = item['field_name']
                    setting_value['value'] = item['value']
                    res_data['settings'].append(setting_value)

            elif count == 1:
                queryset = ParentSetting.objects.get(parent=parent_id, field_name=item['field_name'])
                queryset.field_name = item['field_name']
                queryset.value = item['value']
                queryset.save()

                setting_value['field_name'] = item['field_name']
                setting_value['value'] = item['value']
                res_data['settings'].append(setting_value)

            else:
                error = {}
                error['error'] = "Error: found more that one of the same setting"
                return Response(error)

        return Response(res_data)

class UpdateTutorSettings(APIView):
    """
    POST:
    Description: Updates the tutor settings
    Input:
    {
    "tutor_id": id of tutor,
    "settings": [
            {
                "field_name": string,
                "value": string
            }
        ...
        ]
    }
    Output:
    {
    "tutor_id": id of tutor,
    "settings": [
            {
                "field_name": string,
                "value": string
            }
        ...
        ]
    }
    """
    def post(self, request, format=None):
        tutor_id = request.data['tutor_id']
        settings = request.data['settings']
        res_data = {}
        res_data['tutor_id'] = tutor_id
        res_data['settings'] = []

        for item in settings:
            queryset = TutorSetting.objects.filter(tutor=tutor_id, field_name=item['field_name'])
            count = queryset.count()
            setting_value = {}

            if count == 0:
                data = {
                "tutor": tutor_id,
                "field_name": item['field_name'],
                "value": item['value']
                }

                serializer_class = TutorSettingSerializer(data=data)
                if serializer_class.is_valid():
                    serializer_class.save()

                    setting_value['field_name'] = item['field_name']
                    setting_value['value'] = item['value']
                    res_data['settings'].append(setting_value)

            elif count == 1:
                queryset = TutorSetting.objects.get(tutor=tutor_id, field_name=item['field_name'])
                queryset.field_name = item['field_name']
                queryset.value = item['value']
                queryset.save()

                setting_value['field_name'] = item['field_name']
                setting_value['value'] = item['value']
                res_data['settings'].append(setting_value)

            else:
                error = {}
                error['error'] = "Error: found more that one of the same setting"
                return Response(error)

        return Response(res_data)

class GetParentSettings(APIView):
    """
    POST:
    Description: Get all parent settings given a parent id
    Input:
    {
        "parent_id": id of parent
    }
    Output:
    {
        "settings": [
            {
                "id": id of setting object,
                "parent": id of parent,
                "field_name": string,
                "value": string
            }
            ...
        }
    }
    """
    def post(self, request, format=None):
        res_data = {}
        parent_id = request.data['parent_id']

        queryset = ParentSetting.objects.filter(parent=parent_id)
        parent_setting_serializer = ParentSettingSerializer(queryset, many=True)
        res_data['settings'] = parent_setting_serializer.data

        return Response(res_data)

class GetTutorSettings(APIView):
    """
    Description: Get all tutor settings given a parent id
    Input:
    {
        "tutor_id": id of tutor
    }
    Output:
    {
        "settings": [
            {
                "id": id of setting object,
                "tutor": id of tutor,
                "field_name": string,
                "value": string
            }
            ...
        }
    }
    """
    def post(self, request, format=None):
        res_data = {}
        tutor_id = request.data['tutor_id']

        queryset = TutorSetting.objects.filter(tutor=tutor_id)
        tutor_setting_serializer = TutorSettingSerializer(queryset, many=True)
        res_data['settings'] = tutor_setting_serializer.data

        return Response(res_data)
