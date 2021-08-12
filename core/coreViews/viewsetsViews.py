from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
import requests
import json
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

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
    TutorApplicationSerializer,
    TutorPayoutSerializer,
    GeneralPromoSerializer,
    UniquePromoSerializer,
    ShopItemSerializer,
    AdminSerializer,
    AccountLoggerSerializer,
    AdminTutorMessageSerializer,
    AdminTutorConversationSerializer,
    AdminParentMessageSerializer,
    AdminParentConversationSerializer,
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
    TutorApplication,
    TutorPayout,
    GeneralPromo,
    UniquePromo,
    ShopItem,
    Admin,
    AccountLogger,
    AdminTutorMessage,
    AdminTutorConversation,
    AdminParentMessage,
    AdminParentConversation,
    TutorStrike,
    CreditTracker
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class ParentViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the parent objects
    Output:
    {
        "username": string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "credits": float,
        "status": boolean,
        "phone": string,
        "picture": string
    }
    POST:
    Decription: Adds a parent object to the Database
    Input:
    {
        "username": string,
        "first_name": string,
        "last_name": string,
        "email": string,
        "credits": float,
        "status": boolean,
        "phone": string,
        "picture": string
    }
    """
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

# class ParentView(ListCreateAPIView):
#     """
#     Get all parents:
#         Returns String username, String first_name, String last_name, String email, Float credits, and Boolean status
#     Post a parent:
#         Requires String username, String first_name, String last_name, String email, Float credits, and Boolean status
#     """
#     queryset = Parent.objects.all()
#     serializer_class = ParentSerializer
#     permission_classes = [permissions.IsAuthenticated]

class TutorViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the tutor objects
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
    POST:
    Decription: Adds a tutor object to the Database
    Input:
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
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class ChildViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the child objects
    Output:
    {
        "parent": id of parent,
        "first_name": string,
        "last_name": string,
        "age": integer,
        "year_level": string,
        "school": string
    }
    POST:
    Decription: Adds a child object to the Database
    Input:
    {
        "parent": id of parent,
        "first_name": string,
        "last_name": string,
        "age": integer,
        "year_level": integer,
        "school": string
    }
    """
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class RequestsViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the request objects
    Output:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string,
        "is_favourite": String,
        "subject": String,
        "topics": String,
        "special_request": String
    }
    POST:
    Decription: Adds a request object to the Database
    Input:
    {
        "parent": id of parent,
        "child": id of child,
        "tutor_email": string,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": Datetime,
        "extra_files": string,
        "status": string,
        "is_favourite": String,
        "subject": String,
        "topics": String,
        "special_request": String
    }
    """
    queryset = Requests.objects.all()
    serializer_class = RequestsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head', 'delete']

class SessionViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the session objects
    Output:
    {
        "request": id of request,
        "zoom_link": string,
        "active": string
    }
    POST:
    Decription: Adds a session object to the Database
    Input:
    {
        "request": id of request,
        "zoom_link": string,
        "active": string
    }
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AllFeedbackViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the feedback objects
    Output:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    POST:
    Decription: Adds a feedback object to the Database
    Input:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class FeedbackViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the feedback objects that are not reports
    Output:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    POST:
    Decription: Adds a feedback object to the Database
    Input:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    """
    queryset = Feedback.objects.filter(is_report=False)
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class ReportViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the feedback objects that are reports
    Output:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    POST:
    Decription: Adds a feedback object to the Database
    Input:
    {
        "session": id of session,
        "sender_email": string,
        "receiver_email": string,
        "is_report": boolean,
        "rating": float,
        "content": string
    }
    """
    queryset = Feedback.objects.filter(is_report=True)
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']



class ConversationViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the conversation objects
    Output:
    {
        "session": id of session
    }
    POST:
    Decription: Adds a conversation object to the Database
    Input:
    {
        "session": id of session
    }
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class MessageViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the message objects
    Output:
    {
        "conversation": id of conversation,
        "sender_email": string,
        "receiver_email": string,
        "text": string
    }
    POST:
    Decription: Adds a message object to the Database
    Input:
    {
        "conversation": id of conversation,
        "sender_email": string,
        "receiver_email": string,
        "text": string
    }
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AvailableDaysViewSet (viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the available day objects
    Output:
    {
        "request": id of request,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": float
    }
    POST:
    Decription: Adds an available day object to the Database
    Input:
    {
        "request": id of request,
        "start_date_time": Datetime,
        "end_date_time": Datetime,
        "time": float
    }
    """
    queryset = AvailableDays.objects.all()
    serializer_class = AvailableDaysSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class FavouriteTutorViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the favourite tutor objects
    Output:
    {
        "parent": id of parent,
        "tutor": id of tutor
    }
    POST:
    Decription: Adds a favourite tutor object to the Database
    Input:
    {
        "parent": id of parent,
        "tutor": id of tutor
    }
    """
    queryset = FavouriteTutor.objects.all()
    serializer_class = FavouriteTutorSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class PayMongoTransactionViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all the transaction objects
    Output:
    {
        "parent": id of parent,
        "credits": float,
        "amount": float,
        "method": string
    }
    POST:
    Decription: Adds a transaction object to the Database
    Input:
    {
        "parent": id of parent,
        "credits": float,
        "amount": float,
        "method": string
    }
    """
    queryset = PayMongoTransaction.objects.all()
    serializer_class = PayMongoTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class SubjectViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Gets all subject objects
    Output:
    {
        "subject_field": string
    }
    POST:
    Decription: Add a subject object
    Input:
    {
        "subject_field": string
    }
    """

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

class AdminSettingViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all admin setting objects
    Output:
    {
        "field_name": string,
        "value": string
    }
    POST:
    Decription: Add an admin setting object
    Input:
    {
        "subject_field": string,
        "value": string
    }
    """

    queryset = AdminSetting.objects.all()
    serializer_class = AdminSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class ParentSettingViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all setting objects
    Output:
    {
        "parent": id of parent
        "field_name": string,
        "value": string
    }
    POST:
    Decription: Add a setting object
    Input:
    {
        "parent": id of parent
        "subject_field": string,
        "value": string
    }
    """

    queryset = ParentSetting.objects.all()
    serializer_class = ParentSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorSettingViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all setting objects
    Output:
    {
        "tutor": id of tutor
        "field_name": string,
        "value": string
    }
    POST:
    Decription: Add a setting object
    Input:
    {
        "tutor": id of tutor
        "subject_field": string,
        "value": string
    }
    """

    queryset = TutorSetting.objects.all()
    serializer_class = TutorSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class ParentNotificationViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all setting objects
    Output:
    {
        "tutor": id of tutor
        "field_name": string,
        "value": string
    }
    POST:
    Decription: Add a setting object
    Input:
    {
        "tutor": id of tutor
        "subject_field": string,
        "value": string
    }
    """

    queryset = ParentNotification.objects.all()
    serializer_class = ParentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorNotificationViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all setting objects
    Output:
    {
        "tutor": id of tutor
        "field_name": string,
        "value": string
    }
    POST:
    Decription: Add a setting object
    Input:
    {
        "tutor": id of tutor
        "subject_field": string,
        "value": string
    }
    """

    queryset = TutorNotification.objects.all()
    serializer_class = TutorNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorSubjectViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all tutor - subject relationship objects
    Output:
    {
        "tutor": id of tutor,
        "subject": id of subject
    }
    POST:
    Decription: Add a tutor - subject relationship object
    Input:
    {
        "tutor": id of tutor,
        "subject": id of subject
    }
    """

    queryset = TutorSubject.objects.all()
    serializer_class = TutorSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorApplicationViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all tutor application objects
    Output:
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
    POST:
    Decription: Add a tutor application object
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
    """

    queryset = TutorApplication.objects.all()
    serializer_class = TutorApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorPayoutViewSet(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all tutor application objects
    Output:
    {
        "photo" = String,
        "week_bracket" = String,
        "session" = String,
        "tutor" = [tutor object]
    }
    POST:
    Decription: Add a tutor payout object
    Input:
    {
        "photo" = String,
        "week_bracket" = String,
        "session" = String,
        "tutor" = [tutor object]
    }
    """

    queryset = TutorPayout.objects.all()
    serializer_class = TutorPayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class GeneralPromoViewset(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all General Promotion objects
    Output:
    {
        "promoCode": String,
        "promoName": String,
        "discount": Float,
        "type": shop item object,
        "maxUsage": Integer,
        "usedBy": [parent objects],
        "status": String,
        "promoPeriod": Datetime
    }
    POST:
    Decription: Add a General Promotion object
    Input:
    {
        "promoCode": String,
        "promoName": String,
        "discount": Float,
        "type": shop item object,
        "maxUsage": Integer,
        "usedBy": [parent objects],
        "status": String,
        "promoPeriod": Datetime
    }
    """

    queryset = GeneralPromo.objects.all()
    serializer_class = GeneralPromoSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class UniquePromoViewset(viewsets.ModelViewSet):
    """
    GET:
    Decription: Get all Unique Promotion objects
    Output:
    {
        "promoCode": String,
        "promoName": String,
        "discount": Float,
        "type": shop item object,
        "linkedAccount": parent object,
        "status": String,
        "terminationPeriod": Datetime
    }
    POST:
    Decription: Add a Unique Promotion object
    Input:
    {
        "promoCode": String,
        "promoName": String,
        "discount": Float,
        "type": shop item object,
        "linkedAccount": parent object,
        "status": String,
        "terminationPeriod": Datetime
    }
    """

    queryset = UniquePromo.objects.all()
    serializer_class = UniquePromoSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class ShopItemViewSet(viewsets.ModelViewSet):
    """
    Get:
    Decription: Get all Shop Items objects
    {
        "amount": Float (Price in PHP)
    	"name": String (name of the bundle)
    	"description": String,
        "timesbought": Integer (default at 0)
        "created": datetime of creation
    }
    POST:
    Decription: Add a Shop Item Object
    {
        "amount": Float (Price in PHP)
    	"name": String (name of the bundle)
    	"description": String,
        "timesbought": Integer (default at 0)
        "created": datetime of creation
    }
    """

    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AdminViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AccountLoggerViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = AccountLogger.objects.all()
    serializer_class = AccountLoggerSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AdminParentConversationViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = AdminParentConversation.objects.all()
    serializer_class = AdminParentConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AdminParentMessageViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = AdminParentMessage.objects.all()
    serializer_class = AdminParentMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AdminTutorConversationViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = AdminTutorConversation.objects.all()
    serializer_class = AdminTutorConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class AdminTutorMessageViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = AdminTutorMessage.objects.all()
    serializer_class = AdminTutorMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class TutorStrikeViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = TutorStrike.objects.all()
    serializer_class = TutorStrikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']

class CreditTrackerViewset(viewsets.ModelViewSet):
    """
    GET POST
    """

    queryset = CreditTracker.objects.all()
    serializer_class = CreditTrackerSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'head']
