from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import AdminTutorMessage, AdminTutorConversation, AdminParentMessage, AdminParentConversation, Conversation, Message, Tutor, Parent, Session
from core.serializers import AdminTutorMessageSerializer, AdminTutorConversationSerializer, AdminParentMessageSerializer, AdminParentConversationSerializer, ConversationSerializer, MessageSerializer, ParentSerializer, TutorSerializer, SessionSerializer
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
from django.utils import timezone
import pytz

class TutorChats(APIView):
	"""
	POST:
	Description: Get all id's of those the tutor can chat with
	Input:
	{
		"tutor_id": id of tutor
	}
	Output:
	{
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
	"""
	def post(self, request, format=None):

		#admin
		#active
		#inactive

		tutor_id = request.data['tutor_id']
		tutor = Tutor.objects.get(id=tutor_id)

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

		return Response(conversation_dict)

class ParentChats(APIView):
	"""
	POST:
	Description: Get all id's of those the parent can chat with
	Input:
	{
		"parent_id": id of parent
	}
	Output:
	{
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
	"""
	def post(self, request, format=None):

		parent_id = request.data['parent_id']
		parent = Parent.objects.get(id=parent_id)

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

		return Response(conversation_dict)

class SpecificConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		conversation = Conversation.objects.get(id=conversation_id)

		messages = Message.objects.filter(conversation=conversation_id).order_by('-time_sent')
		messages_serializer = MessageSerializer(messages, many=True)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class GetUnseenFromSpecificConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation
		"receiver": String ('parent' or 'tutor'),
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		receiver = request.data['receiver']
		conversation = Conversation.objects.get(id=conversation_id)

		if receiver == 'tutor':
			messages = Message.objects.filter(conversation=conversation_id, tutor_seen=False).order_by('-time_sent')
			messages_serializer = MessageSerializer(messages, many=True)
		elif receiver == 'parent':
			messages = Message.objects.filter(conversation=conversation_id, parent_seen=False).order_by('-time_sent')
			messages_serializer = MessageSerializer(messages, many=True)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid receiver value'
			return Response(return_info)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class SpecificAdminTutorConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		conversation = AdminTutorConversation.objects.get(id=conversation_id)

		messages = AdminTutorMessage.objects.filter(at_conversation=conversation_id).order_by('-time_sent')
		messages_serializer = AdminTutorMessageSerializer(messages, many=True)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class GetUnseenFromSpecificAdminTutorConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation,
		"receiver": String ('admin' or 'tutor')
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		receiver = request.data['receiver']
		conversation = AdminTutorConversation.objects.get(id=conversation_id)

		if receiver == 'admin':
			messages = AdminTutorMessage.objects.filter(at_conversation=conversation_id, admin_seen=False).order_by('-time_sent')
			messages_serializer = AdminTutorMessageSerializer(messages, many=True)
		elif receiver == 'tutor':
			messages = AdminTutorMessage.objects.filter(at_conversation=conversation_id, tutor_seen=False).order_by('-time_sent')
			messages_serializer = AdminTutorMessageSerializer(messages, many=True)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid receiver value'
			return Response(return_info)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class SpecificAdminParentConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		conversation = AdminParentConversation.objects.get(id=conversation_id)

		messages = AdminParentMessage.objects.filter(ap_conversation=conversation_id).order_by('-time_sent')
		messages_serializer = AdminParentMessageSerializer(messages, many=True)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class GetUnseenFromSpecificAdminParentConversation(APIView):
	"""
	POST:
	Description: Get all messages of a specific conversation
	Input:
	{
		"conversation_id": id of conversation,
		"receiver": String ('admin' or 'parent')
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		receiver = request.data['receiver']
		conversation = AdminParentConversation.objects.get(id=conversation_id)

		if receiver == 'admin':
			messages = AdminParentMessage.objects.filter(ap_conversation=conversation_id, admin_seen=False).order_by('-time_sent')
			messages_serializer = AdminParentMessageSerializer(messages, many=True)
		elif receiver == 'parent':
			messages = AdminParentMessage.objects.filter(ap_conversation=conversation_id, parent_seen=False).order_by('-time_sent')
			messages_serializer = AdminParentMessageSerializer(messages, many=True)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid receiver value'
			return Response(return_info)

		return_info = {}
		return_info['messages'] = messages_serializer.data

		return Response(return_info)

class SeenConversation(APIView):
	"""
	POST:
	Description: Changes all the truth values of the messages of a conversation to True
	Input:
	{
		"conversation_id": id of conversation,
		"looker": String ('parent' or 'tutor')
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		looker = request.data['looker']
		conversation = Conversation.objects.get(id=conversation_id)

		if looker == 'tutor':
			messages = Message.objects.filter(conversation=conversation_id, tutor_seen=False).order_by('-time_sent')
			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.tutor_seen = True
				message.save()
				message_serializer = MessageSerializer(message)
				return_info['messages'].append(message_serializer.data)

			return Response(return_info)
		elif looker == 'parent':
			messages = Message.objects.filter(conversation=conversation_id, parent_seen=False).order_by('-time_sent')

			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.parent_seen = True
				message.save()
				message_serializer = MessageSerializer(message)
				return_info['messages'].append(message_serializer.data)

			return Response(return_info)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid looker value'
			return Response(return_info)

		return_info = {}
		return_info['return_status'] = 'error'
		return_info['return_message'] = 'Error: Unknown Error Occured'
		return Response(return_info)

class SeenAdminTutorConversation(APIView):
	"""
	POST:
	Description: Changes all the truth values of the messages of a conversation to True
	Input:
	{
		"conversation_id": id of conversation
		"looker": String ('admin' or 'tutor')
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		looker = request.data['looker']
		conversation = AdminTutorConversation.objects.get(id=conversation_id)

		if looker == 'admin':
			messages = AdminTutorMessage.objects.filter(at_conversation=conversation_id, admin_seen=False).order_by('-time_sent')
			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.admin_seen = True
				message.save()
				message_serializer = AdminTutorMessageSerializer(message)
				return_info['messages'].append(message_serializer.data)

			return Response(return_info)
		elif looker == 'tutor':
			messages = AdminTutorMessage.objects.filter(at_conversation=conversation_id, tutor_seen=False).order_by('-time_sent')
			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.tutor_seen = True
				message.save()
				message_serializer = AdminTutorMessageSerializer(message)
				return_info['messages'].append(message_serializer.data)

			return Response(return_info)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid looker value'
			return Response(return_info)

		return_info = {}
		return_info['return_status'] = 'error'
		return_info['return_message'] = 'Error: Unknown error occured'
		return Response(return_info)



class SeenAdminParentConversation(APIView):
	"""
	POST:
	Description: Changes all the truth values of the messages of a conversation to True
	Input:
	{
		"conversation_id": id of conversation,
		"looker": String ('parent' or 'admin')
	}
	Output:
	{
		"messages": [message objects]
	}
	"""
	def post(self, request, format=None):

		conversation_id = request.data['conversation_id']
		looker = request.data['looker']
		conversation = AdminParentConversation.objects.get(id=conversation_id)

		if looker == 'admin':
			messages = AdminParentMessage.objects.filter(ap_conversation=conversation_id, admin_seen=False).order_by('-time_sent')

			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.admin_seen = True
				message.save()
				message_serializer = AdminParentMessageSerializer(message)
				return_info['messages'].append(message_serializer.data)
			return Response(return_info)
		elif looker == 'parent':
			messages = AdminParentMessage.objects.filter(ap_conversation=conversation_id, parent_seen=False).order_by('-time_sent')
			messages_serializer = AdminParentMessageSerializer(messages, many=True)
			return_info = {}
			return_info['messages'] = []

			for message in messages:
				message.parent_seen = True
				message.save()
				message_serializer = AdminParentMessageSerializer(message)
				return_info['messages'].append(message_serializer.data)
			return Response(return_info)
		else:
			return_info = {}
			return_info['return_status'] = 'error'
			return_info['return_message'] = 'Error: Invalid looker value'
			return Response(return_info)

		return_info = {}
		return_info['return_status'] = 'error'
		return_info['return_message'] = 'Error: Unknown error occured'
		return Response(return_info)

class SendMessage(APIView):
	"""
	POST:
	Description: Send a message to either parent or tutor
	Input:
	{
		"conversation_id": id of conversation,
		"sender": string ('parent' or 'tutor'),
		"text": string
	}
	Output:
	{
		"message" : message object,
		"return_status" : string ('success' or 'error')
		"return_message" : string
	}
	"""
	def post(self, request, format=None):
		return_info = {}
		return_info['message'] = None

		conversation_id = request.data['conversation_id']
		sender = request.data['sender']
		text = request.data['text']
		timezone.activate(pytz.timezone("Asia/Manila"))
		now = timezone.localtime(timezone.now())

		try:
			convo_ob = Conversation.objects.get(id=conversation_id)
		except:
			return_info['return_status'] = "error"
			return_info['return_message'] = "Error: Conversation does not exist"
			return Response(return_info)

		data = {
    		"conversation": conversation_id,
            "text": text,
			"time_sent": now,
			"sender": sender
        }

		serializer_class = MessageSerializer(data=data)
		if serializer_class.is_valid():
			serializer_class.save()
			return_info['message'] = serializer_class.data
			return_info['return_status'] = "success"
			return_info['return_message'] = "Successfully sent message"
			return Response(return_info)

		return_info['message'] = serializer_class.errors
		return_info['return_status'] = "error"
		return_info['return_message'] = "Error: unknown error when sending message"
		return Response(return_info)

class SendAdminTutorMessage(APIView):
	"""
	POST:
	Description: Send a message to either parent or tutor
	Input:
	{
		"conversation_id": id of conversation,
		"sender": string ('admin' or 'tutor'),
		"text": string
	}
	Output:
	{
		"message" : message object,
		"return_status" : string ('success' or 'error')
		"return_message" : string
	}
	"""
	def post(self, request, format=None):
		return_info = {}
		return_info['message'] = None

		conversation_id = request.data['conversation_id']
		sender = request.data['sender']
		text = request.data['text']
		timezone.activate(pytz.timezone("Asia/Manila"))
		now = timezone.localtime(timezone.now())

		try:
			convo_ob = AdminTutorConversation.objects.get(id=conversation_id)
		except:
			return_info['return_status'] = "error"
			return_info['return_message'] = "Error: Conversation does not exist"
			return Response(return_info)

		data = {
    		"at_conversation": conversation_id,
            "text": text,
			"time_sent": now,
			"sender": sender
        }

		serializer_class = AdminTutorMessageSerializer(data=data)
		if serializer_class.is_valid():
			serializer_class.save()
			return_info['message'] = serializer_class.data
			return_info['return_status'] = "success"
			return_info['return_message'] = "Successfully sent message"
			return Response(return_info)

		return_info['message'] = serializer_class.errors
		return_info['return_status'] = "error"
		return_info['return_message'] = "Error: unknown error when sending message"
		return Response(return_info)

class SendAdminParentMessage(APIView):
	"""
	POST:
	Description: Send a message to either parent or tutor
	Input:
	{
		"conversation_id": id of conversation,
		"sender": string ('admin' or 'parent'),
		"text": string
	}
	Output:
	{
		"message" : message object,
		"return_status" : string ('success' or 'error')
		"return_message" : string
	}
	"""
	def post(self, request, format=None):
		return_info = {}
		return_info['message'] = None

		conversation_id = request.data['conversation_id']
		sender = request.data['sender']
		text = request.data['text']
		timezone.activate(pytz.timezone("Asia/Manila"))
		now = timezone.localtime(timezone.now())

		try:
			convo_ob = AdminParentConversation.objects.get(id=conversation_id)
		except:
			return_info['return_status'] = "error"
			return_info['return_message'] = "Error: Conversation does not exist"
			return Response(return_info)

		data = {
    		"ap_conversation": conversation_id,
            "text": text,
			"time_sent": now,
			"sender": sender
        }

		serializer_class = AdminParentMessageSerializer(data=data)
		if serializer_class.is_valid():
			serializer_class.save()
			return_info['message'] = serializer_class.data
			return_info['return_status'] = "success"
			return_info['return_message'] = "Successfully sent message"
			return Response(return_info)

		return_info['message'] = serializer_class.errors
		return_info['return_status'] = "error"
		return_info['return_message'] = "Error: unknown error when sending message"
		return Response(return_info)
