from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Session, Requests, Parent, Feedback, Tutor
from core.serializers import SessionSerializer, RequestsSerializer, ParentSerializer, FeedbackSerializer, TutorSerializer
from django.core.exceptions import ObjectDoesNotExist
import requests
import json

class ParentReport(APIView):
	"""
	POST:
	Description: Parent makes report for finished session
	Input:
	{
		"session_id": id of session,
		"content": String
	}
	Output:
	{
		"session": id of session,
		"sender_email": String,
		"receiver_email": String,
		"is_report": boolean,
		"content": String
	}
	"""

	def post(self, request, format=None):
		session_id = request.data['session_id']
		session = Session.objects.get(id=session_id)

		request_id = session.request.id
		request_ob = Requests.objects.get(id=request_id)

		if request_ob.status == 'finished':
			parent_id = request_ob.parent.id
			parent = Parent.objects.get(id=parent_id)

			content = request.data['content']

			data = {
				"session": session_id,
				"sender_email": parent.email,
				"receiver_email": request_ob.tutor.email,
				"is_report": True,
				"rating": None,
				"content": content
			}

			feedback_serializer = FeedbackSerializer(data=data)
			if feedback_serializer.is_valid():
				feedback_serializer.save()
				return Response(feedback_serializer.data)
			else:
				return Response(feedback_serializer.errors)

		else:
			return Response('cannot send a report for a session that has not concluded')

class TutorReport(APIView):
	"""
	POST:
	Description: Tutor makes report for finished session
	Input:
	{
		"session_id": id of session,
		"content": String
	}
	Output:
	{
		"session": id of session,
		"sender_email": String,
		"receiver_email": String,
		"is_report": boolean,
		"content": String
	}
	"""

	def post(self, request, format=None):
		session_id = request.data['session_id']
		session = Session.objects.get(id=session_id)

		request_id = session.request.id
		request_ob = Requests.objects.get(id=request_id)

		if request_ob.status == 'finished':
			parent_id = request_ob.parent.id
			parent = Parent.objects.get(id=parent_id)

			content = request.data['content']

			data = {
				"session": session_id,
				"sender_email": request_ob.tutor.email,
				"receiver_email": parent.email,
				"is_report": True,
				"rating": None,
				"content": content
			}

			feedback_serializer = FeedbackSerializer(data=data)
			if feedback_serializer.is_valid():
				feedback_serializer.save()
				return Response(feedback_serializer.data)
			else:
				return Response(feedback_serializer.errors)

		else:
			return Response('cannot send a report for a session that has not concluded')

class ParentFeedback(APIView):
	"""
	POST:
	Description: Parent sends feedback for finished session
	Input:
	{
		"session_id": id of session,
		"rating": float,
		"content": String
	}
	Output:
	{
		"session": id of session,
		"sender_email": String,
		"receiver_email": String,
		"is_report": boolean,
		"content": String
	}
	"""
	def post(self, request, format=None):
		session_id = request.data['session_id']
		session = Session.objects.get(id=session_id)

		request_id = session.request.id
		request_ob = Requests.objects.get(id=request_id)

		if request_ob.status == 'finished':
			parent_id = request_ob.parent.id
			parent = Parent.objects.get(id=parent_id)

			tutor_email = request_ob.tutor.email
			tutor = Tutor.objects.get(email=tutor_email)

			previous_feedback = Feedback.objects.filter(receiver_email=tutor_email).filter(is_report='False')
			previous_feedback_serializer = FeedbackSerializer(previous_feedback, many=True)

			number_of_ratings = 0
			total_of_all_ratings = 0
			for fb in previous_feedback_serializer.data:
				number_of_ratings += 1
				total_of_all_ratings += float(fb['rating'])

			rating = request.data['rating']
			content = request.data['content']

			data = {
				"session": session_id,
				"sender_email": parent.email,
				"receiver_email": tutor_email,
				"is_report": False,
				"rating": rating,
				"content": content
			}

			feedback_serializer = FeedbackSerializer(data=data)
			if feedback_serializer.is_valid():
				feedback_serializer.save()

				#update tutors overall rating
				tutor.rating =  (total_of_all_ratings + rating) / (number_of_ratings + 1)
				tutor.save()

				return Response(feedback_serializer.data)
			else:
				return Response(feedback_serializer.errors)

		else:
			return Response('cannot send a report for a session that has not concluded')

class TutorFeedback(APIView):
	"""
	POST:
	Description: Tutor sends feedback for finished session
	Input:
	{
		"session_id": id of session,
		"content": String
	}
	Output:
	{
		"session": id of session,
		"sender_email": String,
		"receiver_email": String,
		"is_report": boolean,
		"content": String
	}
	"""

	def post(self, request, format=None):
		session_id = request.data['session_id']
		session = Session.objects.get(id=session_id)

		request_id = session.request.id
		request_ob = Requests.objects.get(id=request_id)

		if request_ob.status == 'finished':
			parent_id = request_ob.parent.id
			parent = Parent.objects.get(id=parent_id)

			content = request.data['content']

			data = {
				"session": session_id,
				"sender_email": request_ob.tutor.email,
				"receiver_email": parent.email,
				"is_report": False,
				"rating": None,
				"content": content
			}

			feedback_serializer = FeedbackSerializer(data=data)
			if feedback_serializer.is_valid():
				feedback_serializer.save()
				return Response(feedback_serializer.data)
			else:
				return Response(feedback_serializer.errors)

		else:
			return Response('cannot send a report for a session that has not concluded')
