from django.contrib.auth.models import User, Group
from rest_framework import serializers
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
    GeneralPromo,
    UniquePromo,
    ShopItem,
    Admin,
    AccountLogger,
    TutorStrike,
    AdminTutorMessage,
    AdminTutorConversation,
    AdminParentMessage,
    AdminParentConversation,
    CreditTracker
    )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ParentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Parent
		fields = ['id', 'username', 'first_name', 'last_name', 'email', 'credits', 'status', 'phone', 'picture','files', 'first_time_user', 'referrer_code', 'referrer_method', 'survey', 'other_referrer', 'fake_user']

class TutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ['id', 'username','first_name', 'last_name', 'email', 'school', 'course', 'achievements', 'rating', 'zoominfo', 'status', 'phone', 'picture', 'files', 'bank_name', 'bank_account_name', 'bank_account_type', 'bank_account_number', 'first_time_user', 'birthday', 'fake_user']

class ChildSerializer(serializers.ModelSerializer):
	class Meta:
		model = Child
		fields = ['id', 'parent', 'first_name', 'last_name', 'age', 'year_level', 'school', 'email']

class RequestsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Requests
		fields = ['id', 'parent', 'child', 'time', 'extra_files', 'status', 'is_favourite', 'subject', 'topics', 'special_request', 'fav_tutor', 'time_created', 'declined_tutors', 'declined_reason']

class FeedbackSerializer(serializers.ModelSerializer):
	class Meta:
		model = Feedback
		fields = ['id', 'session', 'sender_email', 'receiver_email', 'is_report', 'rating', 'content']

class SessionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Session
		fields = ['id', 'request', 'tutor_join_link', 'tutee_join_link', 'active', 'start_date_time', 'end_date_time', 'tutor']

class ConversationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Conversation
		fields = ['id', 'session', 'parent', 'tutor', 'active']

class MessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = Message
		fields = ['id', 'conversation', 'sender', 'text', 'time_sent', 'parent_seen', 'tutor_seen']

class AdminParentConversationSerializer(serializers.ModelSerializer):
	class Meta:
		model = AdminParentConversation
		fields = ['id', 'parent']

class AdminParentMessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = AdminParentMessage
		fields = ['id', 'ap_conversation', 'sender', 'text', 'time_sent', 'admin_seen', 'parent_seen']

class AdminTutorConversationSerializer(serializers.ModelSerializer):
	class Meta:
		model = AdminTutorConversation
		fields = ['id', 'tutor']

class AdminTutorMessageSerializer(serializers.ModelSerializer):
	class Meta:
		model = AdminTutorMessage
		fields = ['id', 'at_conversation', 'sender', 'text', 'time_sent', 'admin_seen', 'tutor_seen']

class FavouriteTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Favourite_tutors
		fields = ['id', 'parent', 'tutor']

class AvailableDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDays
        fields = ['id', 'request', 'start_date_time', 'end_date_time']

class PayMongoTransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = PayMongoTransaction
		fields = ['id', 'parent', 'credits', 'amount', 'client_key', 'status', 'date']

class SourcePayMongoTransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = SourcePayMongoTransaction
		fields = ['id', 'parent', 'credits', 'amount', 'src_id', 'pay_id', 'status', 'date']

class BrankasTransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = BrankasTransaction
		fields = ['id', 'parent', 'credits', 'amount', 'transfer_id', 'ref_id', 'status', 'date']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_field']

class AdminSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminSetting
        fields = ['id', 'field_name', 'value']

class ParentSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentSetting
        fields = ['id', 'parent', 'field_name', 'value']

class TutorSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSetting
        fields = ['id', 'tutor', 'field_name', 'value']

class ParentNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentNotification
        fields = ['id', 'parent', 'is_seen', 'notification', 'time']

class TutorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorNotification
        fields = ['id', 'tutor', 'is_seen', 'notification', 'time']

class TutorSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSubject
        fields = ['id', 'tutor', 'subject']

class TutorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorApplication
        fields = ['id', 'first_name', 'last_name', 'sex', 'email', 'subjects', 'achievements', 'tutoring_experience', 'grade_levels', 'identification_photo', 'TOR', 'resume', 'accepted', 'birthday', 'facebook_link', 'school', 'course', 'year_of_graduation', 'other_info', 'phone', 'created', 'bank_name', 'bank_account_name', 'bank_account_type', 'bank_account_number']

class TutorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorPayout
        fields = ['id', 'photo', 'week_bracket', 'session', 'tutor', 'isPaid']

class GeneralPromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralPromo
        fields = ['id', 'promoCode', 'promoName', 'discount', 'type', 'maxUsage', 'usedBy', 'status', 'promoPeriod']

class UniquePromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniquePromo
        fields = ['id', 'promoCode', 'promoName', 'discount', 'type', 'linkedAccount', 'status', 'terminationPeriod']

class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = ['id', 'amount', 'credits', 'name', 'timesBought', 'created', 'archived', 'commission']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'username' ,'email', 'picture']

class AccountLoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountLogger
        fields = ['id', 'time', 'type', 'google_data']

class TutorStrikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorStrike
        fields = ['id', 'tutor', 'time', 'reason', 'session']

class CreditTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTracker
        fields = ['id', 'parent', 'time', 'add_credit', 'subtract_credit']
