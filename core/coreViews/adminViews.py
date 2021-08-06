from rest_framework import permissions
from rest_framework.views import APIView
import requests
import json
import ast
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from core.extra_functions import getStartDateAndEndDateOfWeek, displayErrors, convertDateStringToDate
from django.utils import timezone
import datetime
import pytz
from multiprocessing import Process
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
    TutorApplicationSerializer,
    TutorPayoutSerializer,
    GeneralPromoSerializer,
    UniquePromoSerializer,
    ShopItemSerializer,
    AccountLoggerSerializer,
    AdminTutorMessageSerializer,
    AdminTutorConversationSerializer,
    AdminParentMessageSerializer,
    AdminParentConversationSerializer,
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
    Favourite_tutors,
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
    AccountLogger,
    AdminTutorMessage,
    AdminTutorConversation,
    AdminParentMessage,
    AdminParentConversation,
    CreditTracker
    )

class TutorApplicationToTutorObject(APIView):
    """
    POST:
    Description: turn a tutor application object to a tutor object
    Input:
    {
        "tutor_application_id": id of tutor application,
        "username": String,
    }
    Output:
    {
        "tutor": tutor object,
        "conversation": conversation object,
        "message": message object
    }
    """
    def post(self, request, format=None):
        tutor_application_id = request.data['tutor_application_id']
        username = request.data['username']
        # school = request.data['school']
        # course = request.data['course']
        # achievements = request.data['achievements']
        # zoominfo = request.data['zoominfo']
        # status = request.data['status']
        # phone = request.data['phone']
        # picture = request.data['picture']

        tutor_application = TutorApplication.objects.get(id=tutor_application_id)

        #make the tutor object
        data = {
            'username': username,
            'first_name': tutor_application.first_name,
            'last_name': tutor_application.last_name,
            'email': tutor_application.email,
            'school': tutor_application.school,
            'course': tutor_application.course,
            'achievements': tutor_application.achievements,
            'rating': 0,
            'zoominfo': zoominfo,
            'status': True,
            'phone': tutor_application.phone,
            'picture': tutor_application.identification_photo,
            'bank_name': tutor_application.bank_name,
        	'bank_account_number': tutor_application.bank_account_number,
        	'bank_account_name': tutor_application.bank_account_name,
        	'bank_account_type': tutor_application.bank_account_type,
            'birthday': tutor_application.birthday
        }

        tutor_serializer_class = TutorSerializer(data=data)
        if tutor_serializer_class.is_valid():
            tutor_serializer_class.save()
            return_info = {}
            return_info['tutor'] = tutor_serializer_class.data

            #create conversation with admin and send a default message
            conversation = Conversation(session=None)
            conversation.save()
            conversation_serializer_class = ConversationSerializer(conversation)
            return_info['conversation'] = conversation_serializer_class.data

            message = Message(conversation=conversation,
                sender_email='admin',
                receiver_email=tutor_application.email,
                text='Default message from admin to tutor')
            message.save()
            message_serializer_class = MessageSerializer(message)
            return_info['message'] = message_serializer_class.data

            tutor_application.accepted = True
            tutor_application.save()
            return Response(return_info)
        else:
            return Response(tutor_serializer_class.errors)

class AllAdminDetails(APIView):
    """
    GET:
    Description: All info needed for tutor view
    input:
    {
        Nothing
    }
    Output:
    {
        "parents": [Parent Objects],
        "children": [Children Objects],
        "tutors": [Tutor Objects],
        "payments": [PayMongoTransaction Objects],
        "payouts": [TutorPayout Objects],
        "business_stats":{
            "GMV": Float
            "NET_REVENUE": Float
            "NET_REVENUE_CMGR": Float
            "USER_RETENTION": Float
            "BOUGHT": Float
            "USED": Float
        } ,
        "feedbacks": [Feedback Objects],
        "reports": [Report Objects],
        "parent_conversations": {
            "parent": [parent objects],
            "conversation": [Parent Admin Conversation Objects]
        },
        "tutor_conversations": {
            "parent": [parent objects],
            "conversation": [Tutor Admin Conversation Objects]
        },
        "conversations": [Conversation Objects],
        "gen_promos": [GeneralPromo Objects],
        "uni_promos": [UniquePromo Objects],
        "requests": {
            "pending": [Request objects] that are pending,
            "accepted": [Request objects] that are accepted,
            "finished": [Request objects] that are finished,
            "cancelled": [Request objects] that are cancelled
        }
        "sessions": [Session Objects],
        "shop_items": [shop item objects],
        "tutor_applications": [TutorApplication objects],
        "logs": [AccountLogger Objects],
        "credit_tracker": [CreditTracker Objects]
    }
    """
    def get(self, request, format=None):
        return_info = {}

        # Get All parent, children, tutor Objects
        parent_obs = Parent.objects.all()
        serializer_class = ParentSerializer(parent_obs, many=True)
        return_info['parents'] = serializer_class.data

        queryset = Child.objects.all()
        serializer_class = ChildSerializer(queryset, many=True)
        return_info['children'] = serializer_class.data

        queryset = Tutor.objects.all()
        serializer_class = TutorSerializer(queryset, many=True)
        return_info['tutors'] = serializer_class.data

        # Get All Payment transactions
        queryset = PayMongoTransaction.objects.all()
        serializer_class = PayMongoTransactionSerializer(queryset, many=True)
        return_info['payments'] = serializer_class.data

        # Get All Tutor payouts
        queryset = TutorPayout.objects.all()
        serializer_class = TutorPayoutSerializer(queryset, many=True)
        return_info['payouts'] = serializer_class.data

        # Get GetBusinessStatistics
        business_stats = {}

        GMV = 0 # price * hours
        NET_REVENUE = 0 # commission * hours
        NET_REVENUE_CMGR = 0 # FOR V1.5
        USER_RETENTION = 0 # FOR V1.5
        PAID_CAC = 0 # How many people actually bought after free trial

        allshopitems = ShopItem.objects.all()


        for item in allshopitems:
            price = ( item.amount / item.credits ) * ( item.credits * item.timesBought )
            GMV = GMV + price

        for item in allshopitems:
            price = ( item.commission ) * ( item.credits * item.timesBought )
            NET_REVENUE = NET_REVENUE + price

        first_buy = 0
        first_use = 0
        total_parents = 0

        for parent_ob in parent_obs:
            if parent_ob.first_buy == True:
                first_buy = first_buy + 1

            if parent_ob.first_use == True:
                first_use = first_use + 1

            total_parents = total_parents + 1


        business_stats['GMV'] = GMV
        business_stats['NET_REVENUE'] = NET_REVENUE
        business_stats['NET_REVENUE_CMGR'] = NET_REVENUE_CMGR
        business_stats['USER_RETENTION'] = USER_RETENTION
        try:
            business_stats['BOUGHT'] = (first_buy / total_parents) * 100
            business_stats['BOUGHT'] = str(business_stats['BOUGHT']) + '%'
        except:
            business_stats['BOUGHT'] = 0
        try:
            business_stats['USED'] = (first_use / total_parents) * 100
        except:
            business_stats['USED'] = 0
        business_stats['USED'] = str(business_stats['USED']) + '%'

        return_info['business_stats'] = business_stats

        # Get all feedbacks
        queryset = Feedback.objects.filter(is_report=False)
        serializer_class = FeedbackSerializer(queryset, many=True)
        return_info['feedbacks'] = serializer_class.data

        # Get all reports
        queryset = Feedback.objects.filter(is_report=True)
        serializer_class = FeedbackSerializer(queryset, many=True)
        return_info['reports'] = serializer_class.data

        # Get all conversations
        queryset = Conversation.objects.all()
        serializer_class = ConversationSerializer(queryset, many=True)
        return_info['conversations'] = serializer_class.data

        # Get all conversations
        queryset = AdminParentConversation.objects.all()
        ap_convo = []
        for convo in queryset:
            convo_ob = {}
            p_ob = Parent.objects.get(id=convo.parent.id)
            p_ob_serializer = ParentSerializer(p_ob)
            serializer_class = AdminParentConversationSerializer(convo)
            convo_ob['conversation'] = serializer_class.data
            convo_ob['parent'] = p_ob_serializer.data
            ap_convo.append(convo_ob)

        return_info['parent_conversations'] = ap_convo

        # Get all conversations
        queryset = AdminTutorConversation.objects.all()
        at_convo = []
        for convo in queryset:
            convo_ob = {}
            t_ob = Tutor.objects.get(id=convo.tutor.id)
            t_ob_serializer = TutorSerializer(t_ob)
            serializer_class = AdminTutorConversationSerializer(convo)
            convo_ob['conversation'] = serializer_class.data
            convo_ob['tutor'] = t_ob_serializer.data
            at_convo.append(convo_ob)

        return_info['tutor_conversations'] = at_convo

        # Get all general promo codes
        queryset = GeneralPromo.objects.all()
        serializer_class = GeneralPromoSerializer(queryset, many=True)
        return_info['gen_promos'] = serializer_class.data

        # Get all unique promo codes
        queryset = UniquePromo.objects.all()
        serializer_class = UniquePromoSerializer(queryset, many=True)
        return_info['uni_promos'] = serializer_class.data

        # Get all requests
        requests_info = {}

        queryset = Requests.objects.filter(status='pending').order_by('time_created')
        serializer_class = RequestsSerializer(queryset, many=True)
        requests_info['pending'] = serializer_class.data

        queryset = Requests.objects.filter(status='accepted').order_by('time_created')
        serializer_class = RequestsSerializer(queryset, many=True)
        requests_info['accepted'] = serializer_class.data

        queryset = Requests.objects.filter(status='finished').order_by('time_created')
        serializer_class = RequestsSerializer(queryset, many=True)
        requests_info['finished'] = serializer_class.data

        queryset = Requests.objects.filter(status='cancelled').order_by('time_created')
        serializer_class = RequestsSerializer(queryset, many=True)
        requests_info['cancelled'] = serializer_class.data

        queryset = AvailableDays.objects.all()
        serializer_class = AvailableDaysSerializer(queryset, many=True)
        requests_info['availabledays'] = serializer_class.data

        return_info['requests'] = requests_info

        #TEMP REMOVE
        # Get all session objects
        queryset = Session.objects.filter(active=True).order_by('start_date_time')
        serializer_class = SessionSerializer(queryset, many=True)
        # return_info['active_sessions'] = serializer_class.data
        return_info['active_sessions'] = []

        queryset = Session.objects.filter(active=False).order_by('start_date_time')
        serializer_class = SessionSerializer(queryset, many=True)
        # return_info['inactive_sessions'] = serializer_class.data
        return_info['inactive_sessions'] = []

        queryset = ShopItem.objects.all()
        serializer_class = ShopItemSerializer(queryset, many=True)
        return_info['shop_items'] = serializer_class.data

        queryset = TutorApplication.objects.all()
        serializer_class = TutorApplicationSerializer(queryset, many=True)
        return_info['tutor_applications'] = serializer_class.data

        queryset = AccountLogger.objects.order_by('-time')[:20]
        serializer_class = AccountLoggerSerializer(queryset, many=True)
        logs_data = []
        for log in serializer_class.data:
            google_data = log['google_data']
            google_data_dict = ast.literal_eval(google_data)
            log['google_data'] = google_data_dict
            logs_data.append(log)
        return_info['logs'] = logs_data

        queryset = Subject.objects.all()
        serializer_class = SubjectSerializer(queryset, many=True)
        return_info['subjects'] = serializer_class.data

        queryset = Favourite_tutors.objects.all()
        serializer_class = FavouriteTutorSerializer(queryset, many=True)
        return_info['fav_tutors'] = serializer_class.data

        queryset = CreditTracker.objects.all()
        serializer_class = CreditTrackerSerializer(queryset, many=True)
        return_info['credit_tracker'] = serializer_class.data

        return Response(return_info)


class UploadReceiptForPayout(APIView):
    """
    POST:
    Description: Uploads a photo and makes the week bracket of a tutor paid
    input:
    {
        "tutor_id": id of Tutor,
        "week_bound": string (ex. 2020-11-21/2020-11-27),
        "photo": string (photo url)
    }
    Output:
    {
        "payout": TutorPayout object that was updated
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['payout'] = None

        tutor_id = request.data['tutor_id']
        week_bracket = request.data['week_bound']
        photo = request.data['photo']

        try:
            payout_ob = TutorPayout.objects.get(tutor=tutor_id, week_bracket=week_bracket)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Payout object not found"
            return Response(return_info)

        if(payout_ob == True):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Tutor has already been paid"
            payout_ob_ser = TutorPayoutSerializer(payout_ob)
            return_info['payout'] = payout_ob_ser.data
            return Response(return_info)

        payout_ob.photo = photo
        payout_ob.isPaid = True
        payout_ob.save()
        payout_ob_ser = TutorPayoutSerializer(payout_ob)
        return_info['payout'] = payout_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully uploaded photo for the tutor"

        return Response(return_info)



class CreateGeneralPromoCode(APIView):
    """
    POST:
    Description: Creates a general promocode
    input:
    {
        "promoCode": String,
    	"promoName": String,
    	"discount": Float (value from 0.0 to 1.0),
    	"type": id of shop item object
    	"maxUsage": Int,
    	"promoPeriod": Date (ex. 2020-12-24T22:38:00.000Z)
    }
    output:
    {
        "general_promo": GeneralPromo object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['general_promo'] = None

        promoCode = request.data['promoCode']
        promoName = request.data['promoName']
        discount = float(request.data['discount'])
        type = request.data['type']
        maxUsage = int(request.data['maxUsage'])
        promoPeriod = convertDateStringToDate(request.data['promoPeriod'])

        genString = "GEN-" + promoCode

        data = {
            "promoCode": genString,
        	"promoName": promoName,
        	"discount":discount,
        	"type": type,
        	"maxUsage": maxUsage,
        	"usedBy" : [],
        	"status": True,
        	"promoPeriod": promoPeriod
        }

        promo_serializer = GeneralPromoSerializer(data=data)
        if promo_serializer.is_valid():
            promo_serializer.save()
            return_info['general_promo'] = promo_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully created a General Promotion Code"
            return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = displayErrors(serializer_class.errors)
            return Response(return_info)

class CreateUniquePromoCode(APIView):
    """
    POST:
    Description: Creates a general promocode
    input:
    {
        "promoCode": String,
    	"promoName": String,
    	"discount": Float (value from 0.0 to 1.0),
    	"type": id of shop item object
    	"linkedAccount": id of Parent,
    	"terminationPeriod": Date (ex. 2020-12-24T22:38:00.000Z)
    }
    output:
    {
        "unique_promo": GeneralPromo object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['unique_promo'] = None

        promoCode = request.data['promoCode']
        promoName = request.data['promoName']
        discount = float(request.data['discount'])
        type = request.data['type']
        linkedAccount = request.data['linkedAccount']
        terminationPeriod = convertDateStringToDate(request.data['terminationPeriod'])

        uniString = "UNI-" + promoCode

        data = {
            "promoCode": uniString,
        	"promoName": promoName,
        	"discount":discount,
        	"type": type,
        	"linkedAccount": linkedAccount,
        	"status": True,
        	"terminationPeriod": terminationPeriod
        }

        promo_serializer = UniquePromoSerializer(data=data)
        if promo_serializer.is_valid():
            promo_serializer.save()
            return_info['unique_promo'] = promo_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully created a Unique Promotion Code"
            return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = displayErrors(serializer_class.errors)
            return Response(return_info)

class DisableParent(APIView):
    """
    POST:
    Description: Makes a Parent disabled
    Input:
    {
        "parent_id": id of parent
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

        if (parent_ob.status == False):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent account already disabled"
            return Response(return_info)

        parent_ob.status = False
        parent_ob.save()
        parent_ob_ser = ParentSerializer(parent_ob)
        return_info['parent'] = parent_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully disabled the parent account of " + parent_ob.first_name

        return Response(return_info)

class DisableTutor(APIView):
    """
    POST:
    Description: Makes a tutor disabled
    Input:
    {
        "tutor_id": id of tutor
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

        if (tutor_ob.status == False):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Tutor account already disabled"
            return Response(return_info)

        tutor_ob.status = False
        tutor_ob.save()
        tutor_ob_ser = TutorSerializer(tutor_ob)
        return_info['tutor'] = tutor_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully disabled the tutor account of " + tutor_ob.first_name

        return Response(return_info)

class EnableParent(APIView):
    """
    POST:
    Description: Makes a parent enabled
    Input:
    {
        "parent_id": id of parent
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

        if (parent_ob.status == True):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Parent account already enabled"
            return Response(return_info)

        parent_ob.status = True
        parent_ob.save()
        parent_ob_ser = ParentSerializer(parent_ob)
        return_info['parent'] = parent_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully enabled the parent account of " + parent_ob.first_name


        return Response(return_info)

class EnableTutor(APIView):
    """
    POST:
    Description: Makes a tutor enabled
    Input:
    {
        "tutor_id": id of tutor
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

        if (tutor_ob.status == True):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Tutor account already enabled"
            return Response(return_info)

        tutor_ob.status = True
        tutor_ob.save()
        tutor_ob_ser = TutorSerializer(tutor_ob)
        return_info['tutor'] = tutor_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully enabled the tutor account of " + tutor_ob.first_name


        return Response(return_info)

class CreateShopItem(APIView):
    """
    POST:
    Description: Adds a shop item for users to buy
    Input:
    {
        "amount": Float (Price in PHP)
    	"name": String (name of the bundle),
        "credits": Integer (amount of credits a parent will get)
    	"description": String,
        "commission": Float (Price in PHP)
    }
    Output:
    {
        "shop_item": shop item object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['shop_item'] = None

        try:
            amount = float(request.data['amount'])
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Amount given is not float type"

        try:
            commission = float(request.data['commission'])
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "commission amount given is not float type"

        try:
            credits = int(request.data['credits'])
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "credits given is not int type"

        name = request.data['name']
        description = request.data['description']

        timezone.activate(pytz.timezone("Asia/Manila"))
        data = {
            "amount": amount,
        	"name": name,
            "credits": credits,
        	"description":description,
        	"timesBought": 0,
        	"created": timezone.localtime(timezone.now()),
            "archived": False,
            "commission": commission
        }

        sitem_serializer = ShopItemSerializer(data=data)
        if sitem_serializer.is_valid():
            sitem_serializer.save()
            return_info['shop_item'] = sitem_serializer.data
            return_info['return_status'] = "success"
            return_info['return_message'] = "Successfully created a Shop Item"
            return Response(return_info)
        else:
            return_info['return_status'] = "error"
            return_info['return_message'] = displayErrors(sitem_serializer.errors)
            return Response(return_info)

class ArchiveShopItem(APIView):
    """
    POST:
    Description: Archives a shop item
    Input:
    {
        "shop_item_id": id of shop item object
    }
    Output:
    {
        "shop_item": parent object,
        "return_status": string,
        "return_message": string
    }
    """
    def post(self, request, format=None):
        return_info = {}
        return_info['shop_item'] = None

        sitem_id = request.data['shop_item_id']

        try:
            sitem = ShopItem.objects.get(id=sitem_id)
        except:
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Shop Item not found"
            return Response(return_info)

        if (sitem.archived == True):
            return_info['return_status'] = "error"
            return_info['return_message'] = "Error: Shop Item already archived"
            return Response(return_info)

        sitem.archived = True
        sitem.save()
        sitem_ob_ser = ShopItemSerializer(sitem)
        return_info['shop_item'] = sitem_ob_ser.data
        return_info['return_status'] = "success"
        return_info['return_message'] = "Successfully archived shop item " + sitem.name

        return Response(return_info)


class EmailTutors(APIView):
    def post(self, request, format=None):
        tutors = Tutor.objects.all()

        tutor_emails = []
        message = request.data['message']
        subject = request.data['subject']

        for tutor in tutors:
            tutor_emails.append(tutor.email)

        p = Process(target=SendEmail, args=(subject, message, tutor_emails))
        p.start()
