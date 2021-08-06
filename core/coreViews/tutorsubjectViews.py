from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Tutor, Subject, TutorSubject
from core.serializers import TutorSubjectSerializer
from django.core.exceptions import ObjectDoesNotExist
import requests
import json

class AddTutorSubjects(APIView):
    """
    POST
    Description: Add or Update the subjects a tutor can teach
    Input:
    {
        "tutor_id": id of tutor,
        "subjects": [
            {
                "subject": id of subject
            }
            ...
        ]
    }
    Output:
    {
        "tutor_id": id of tutor,
        "subjects": [
            {
                "subject": id of subject
                "subject_field": string (subject)
            }
            ...
        ]
        "exists": [
            {
                "id": id of tutorsubject object,
                "tutor": id of tutor,
                "subject": id of subject
            }
            ...
        ]
    }
    """
    def post(self, request, format=None):
        subjects = request.data['subjects']
        tutor_id = request.data['tutor_id']
        res_data = {}
        res_data['tutor_id'] = tutor_id
        res_data['subjects'] = []
        res_data['exists'] = []

        for subject in subjects:
            subject_id = subject['subject']
            queryset = TutorSubject.objects.filter(tutor=tutor_id, subject=subject_id)
            count = queryset.count()
            subject_val = {}

            if count == 0:
                data = {
                "tutor": tutor_id,
                "subject": subject['subject']
                }

                serializer_class = TutorSubjectSerializer(data=data)
                if serializer_class.is_valid():
                    serializer_class.save()

                    queryVal = Subject.objects.get(id=subject['subject'])
                    subject_val['subject_id'] = subject['subject']
                    subject_val['subject_field'] = queryVal.subject_field
                    res_data['subjects'].append(subject_val)

            elif count == 1:
                queryset = TutorSubject.objects.get(tutor=tutor_id, subject=subject_id)
                serializer_class = TutorSubjectSerializer(queryset)
                res_data['exists'].append(serializer_class.data)

            else:
                error = {}
                error['error'] = "Error: found more that one of the same subject"
                return Response(error)

        return Response(res_data)

class DeleteTutorSubjects(APIView):
    """
    POST
    Description: Delete the subjects a tutor can teach
    Input:
    {
        "tutor_id": id of tutor,
        "subjects": [
            {
                "subject": id of subject
            }
            ...
        ]
    }
    Output:
    {
        "tutor_id": id of tutor,
        "deleted_subjects": [
            {
                "subject": id of subject
            }
            ...
        ]
    }
    """
    def post(self, request, format=None):
        subjects = request.data['subjects']
        tutor_id = request.data['tutor_id']
        res_data = {}
        res_data['tutor_id'] = tutor_id
        res_data['deleted_subjects'] = []

        for subject in subjects:
            subject_id = subject['subject']
            queryset = TutorSubject.objects.filter(tutor=tutor_id, subject=subject_id)
            count = queryset.count()
            subject_val = {}

            if count == 0:
                error = {}
                error['error'] = "Error: Tutor does not teach subject with subject id: " + subject_id
                return Response(error)

            elif count == 1:
                subject_val = {}

                queryset = TutorSubject.objects.get(tutor=tutor_id, subject=subject_id)
                queryVal = Subject.objects.get(id=subject['subject'])

                subject_val['subject_id'] = subject['subject']
                subject_val['subject_field'] = queryVal.subject_field
                res_data['deleted_subjects'].append(subject_val)

                queryset.delete()

            else:
                error = {}
                error['error'] = "Error: found more that one of the same subject"
                return Response(error)

        return Response(res_data)
