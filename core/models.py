from django.db import models
from django.utils import timezone
import django
import pytz
import uuid
from django.db.models import JSONField

# Fixing the timezone
timezone.activate(pytz.timezone("Asia/Manila"))
# Create your models here.
class Subject(models.Model):
	subject_field = models.CharField(max_length=80)
	available = models.BooleanField(default=True)

class AdminSetting(models.Model):
	field_name = models.CharField(max_length=80)
	value = models.CharField(max_length=100)

class Admin(models.Model):
	username = models.CharField(max_length=100) #take this out change to email
	email = models.CharField(max_length=100, default = '')
	picture = models.TextField(default='', blank=True, null=True)

class Parent(models.Model):
	username = models.CharField(max_length=100) #take this out change to email
	id_str = models.UUIDField(default=uuid.uuid4, editable=False)
	first_name = models.CharField(max_length=80, default = '')
	last_name = models.CharField(max_length=80, default = '')
	email = models.CharField(max_length=100, default = '')
	credits = models.FloatField(default = 0)
	status = models.BooleanField(default = True)
	phone = models.CharField(max_length=80, default = '', blank=True, null=True)
	picture = models.TextField(default='', blank=True, null=True)
	files = models.CharField(max_length=100, default = '')
	first_buy = models.BooleanField(default=False)
	first_use = models.BooleanField(default=False)
	first_time_user = models.BooleanField(default=True)
	fake_user = models.BooleanField(default=False)
	referrer_code = models.CharField(max_length=20, default = '', blank=True, null=True)
	referrer_method = models.CharField(max_length=20, default = '', blank=True, null=True)
	other_referrer = models.CharField(max_length=20, default = '', blank=True, null=True)
	survey = JSONField(blank=True, null=True)
	# converted = models.BooleanField(default=False)
	#payment methods #fix when payment methods are figured out

class ParentSetting(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	field_name = models.CharField(max_length=80)
	value = models.CharField(max_length=100)

class Child(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	id_str = models.UUIDField(default=uuid.uuid4, editable=False)
	email = models.CharField(max_length=80, default = '', blank=True, null=True)
	first_name = models.CharField(max_length=80)
	last_name = models.CharField(max_length=80, default = '', blank=True, null=True)
	age = models.IntegerField(blank=True, null=True)
	year_level = models.CharField(max_length=80)
	school = models.CharField(max_length=200, blank=True, null=True)

class Tutor(models.Model):
	username = models.CharField(max_length=100, default ='') #take this out change to email
	id_str = models.UUIDField(default=uuid.uuid4, editable=False)
	first_name = models.CharField(max_length=80, default = '')
	last_name = models.CharField(max_length=80, default = '')
	email = models.CharField(max_length=100, default = '')
	school = models.CharField(max_length=100, default ='', blank=True, null=True)
	course = models.CharField(max_length=100, default ='', blank=True, null=True)
	achievements = models.TextField(default ='', blank=True, null=True)
	rating = models.FloatField(default = 0)
	status = models.BooleanField(default = True)
	phone = models.CharField(max_length=80, default = '', blank=True, null=True)
	picture = models.TextField(default='', blank=True, null=True)
	files = models.CharField(max_length=100, default = '')
	bank_name = models.CharField(max_length=200, blank=True, null=True)
	bank_account_number = models.CharField(max_length=200, blank=True, null=True)
	bank_account_name = models.CharField(max_length=200, blank=True, null=True)
	bank_account_type = models.CharField(max_length=200, blank=True, null=True)
	birthday = models.DateTimeField(default=django.utils.timezone.now, blank=True, null=True)
	first_time_user = models.BooleanField(default=True)
	fake_user = models.BooleanField(default=False)

class TutorSetting(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	field_name = models.CharField(max_length=80)
	value = models.CharField(max_length=100)

class FavouriteTutor(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)

class Requests(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	child = models.ForeignKey(Child, on_delete=models.CASCADE)
	fav_tutor = models.ForeignKey(Tutor, blank=True, null=True, on_delete=models.CASCADE, related_name='favourite')
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	declined_tutors = models.ManyToManyField(Tutor, related_name='declined_tutors')
	declined_reason = models.CharField(max_length=1000, blank=True, null=True)
	time = models.IntegerField(default = 0)
	extra_files = models.CharField(max_length=200, blank=True, null=True)
	status = models.CharField(max_length=50)
	is_favourite = models.BooleanField(default=False)
	topics = models.CharField(max_length=200, default="", blank=True, null=True)
	special_request = models.CharField(max_length=200, blank=True, null=True)
	time_created = models.DateTimeField(default = django.utils.timezone.now)

class Session(models.Model):
	request = models.ForeignKey(Requests, on_delete=models.CASCADE)
	tutor_join_link = models.CharField(max_length=1000, default = '')
	tutee_join_link = models.CharField(max_length=1000, default = '')
	active = models.CharField(max_length=50)
	start_date_time = models.DateTimeField(default = django.utils.timezone.now)
	end_date_time = models.DateTimeField(default = django.utils.timezone.now)
	tutor = models.ForeignKey(Tutor, blank=True, null=True, on_delete=models.CASCADE)

class Conversation(models.Model):
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	active = models.BooleanField(default = True)

class Message(models.Model):
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
	text = models.TextField()
	time_sent = models.DateTimeField(default = django.utils.timezone.now)
	parent_seen = models.BooleanField(default = False)
	tutor_seen = models.BooleanField(default = False)
	sender = models.CharField(max_length=200)

class AdminParentConversation(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

class AdminParentMessage(models.Model):
	ap_conversation = models.ForeignKey(AdminParentConversation, on_delete=models.CASCADE)
	text = models.TextField()
	time_sent = models.DateTimeField(default = django.utils.timezone.now)
	admin_seen = models.BooleanField(default = False)
	parent_seen = models.BooleanField(default = False)
	sender = models.CharField(max_length=200)

class AdminTutorConversation(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)

class AdminTutorMessage(models.Model):
	at_conversation = models.ForeignKey(AdminTutorConversation, on_delete=models.CASCADE)
	text = models.TextField()
	time_sent = models.DateTimeField(default = django.utils.timezone.now)
	admin_seen = models.BooleanField(default = False)
	tutor_seen = models.BooleanField(default = False)
	sender = models.CharField(max_length=200)

class Feedback(models.Model):
	session = models.ForeignKey(Session, on_delete=models.CASCADE)
	sender_email = models.CharField(max_length=200)
	receiver_email = models.CharField(max_length=200)
	is_report = models.BooleanField()
	rating = models.FloatField(default = 0, blank=True, null=True)
	content = models.CharField(max_length= 1000)

class PayMongoTransaction(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	client_key = models.TextField()
	credits = models.FloatField(default = 0)
	amount = models.FloatField(default = 0)
	status = models.BooleanField(default = False)
	date = models.DateTimeField(default = django.utils.timezone.now)

class SourcePayMongoTransaction(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	src_id = models.TextField()
	pay_id = models.TextField()
	credits = models.FloatField(default = 0)
	amount = models.FloatField(default = 0)
	status = models.BooleanField(default = False)
	date = models.DateTimeField(default = django.utils.timezone.now)

class BrankasTransaction(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	transfer_id = models.TextField()
	ref_id = models.TextField()
	credits = models.FloatField(default = 0)
	amount = models.FloatField(default = 0)
	status = models.BooleanField(default = False)
	date = models.DateTimeField(default = django.utils.timezone.now)

class AvailableDays(models.Model):
	request = models.ForeignKey(Requests, on_delete=models.CASCADE)
	start_date_time = models.DateTimeField(default = django.utils.timezone.now)
	end_date_time = models.DateTimeField(default = django.utils.timezone.now)

class ParentNotification(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	is_seen = models.BooleanField(default=False)
	notification = models.CharField(max_length=1000)
	time = models.DateTimeField(default = django.utils.timezone.now)

class TutorNotification(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	is_seen = models.BooleanField(default=False)
	notification = models.CharField(max_length=1000)
	time = models.DateTimeField(default = django.utils.timezone.now)

class TutorSubject(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

class TutorApplication(models.Model):
	first_name = models.CharField(max_length=80, default = '')
	last_name = models.CharField(max_length=80, default = '')
	sex = models.CharField(max_length=10, default = '')
	email = models.CharField(max_length=100, default = '')
	subjects = models.CharField(max_length=200, default = '')
	achievements = models.CharField(max_length=500, default ='', blank=True)
	tutoring_experience = models.CharField(max_length=1000, default = '')
	grade_levels = models.CharField(max_length=1000, default = '')
	identification_photo = models.CharField(max_length=1000, default = '')
	TOR = models.CharField(max_length=1000, default = '', blank=True, null=True)
	resume = models.CharField(max_length=1000, default = '', blank=True, null=True)
	accepted = models.BooleanField(default = False)
	birthday = models.DateTimeField(default = django.utils.timezone.now)
	facebook_link = models.CharField(max_length=1000, default = '')
	school = models.CharField(max_length=100, default ='')
	course = models.CharField(max_length=100, default ='')
	year_of_graduation = models.IntegerField()
	other_info = models.CharField(max_length=1000, default = '', blank=True, null=True)
	created = models.DateTimeField(default = django.utils.timezone.now)
	bank_name = models.CharField(max_length=200)
	bank_account_number = models.CharField(max_length=200)
	bank_account_name = models.CharField(max_length=200)
	bank_account_type = models.CharField(max_length=200)

class TutorPayout(models.Model):
	photo = models.CharField(max_length=1000, default = '')
	week_bracket = models.CharField(max_length=200)
	session = models.ManyToManyField(Session, related_name='sessions')
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	isPaid = models.BooleanField(default = False)

class ShopItem(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False)
	amount = models.IntegerField()
	name = models.CharField(max_length=1000)
	credits = models.IntegerField()
	description = models.CharField(max_length=1000, blank=True, null=True)
	timesBought = models.IntegerField(default=0)
	created = models.DateTimeField(default = django.utils.timezone.now)
	archived = models.BooleanField(default = False)
	commission = models.IntegerField()

class GeneralPromo(models.Model):
	promoCode = models.CharField(max_length=1000, unique=True)
	promoName = models.CharField(max_length=1000)
	discount = models.FloatField()
	type = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
	maxUsage = models.IntegerField()
	usedBy = models.ManyToManyField(Parent, blank=True, related_name='used_by')
	status = models.BooleanField(default=True)
	promoPeriod = models.DateTimeField(default = django.utils.timezone.now)

class UniquePromo(models.Model):
	promoCode = models.CharField(max_length=1000, unique=True)
	promoName = models.CharField(max_length=1000)
	discount = models.FloatField()
	type = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
	linkedAccount = models.ForeignKey(Parent, on_delete=models.CASCADE)
	status = models.BooleanField(default=True)
	terminationPeriod = models.DateTimeField(default = django.utils.timezone.now)

class AccountLogger(models.Model):
	time = models.DateTimeField(default = django.utils.timezone.now)
	type = models.CharField(max_length=100)
	google_data = models.TextField()

class TutorStrike(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	time = models.DateTimeField(default = django.utils.timezone.now)
	reason = models.TextField()
	session = models.ForeignKey(Session, on_delete=models.CASCADE)

class CreditTracker(models.Model):
	parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
	time = models.DateTimeField(default = django.utils.timezone.now)
	add_credit = models.IntegerField()
	subtract_credit = models.IntegerField()
