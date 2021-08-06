from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.utils import timezone
from core.models import Tutor, Parent, Message, AdminSetting, TutorPayout, Conversation, ParentNotification, TutorNotification, Requests, Session
from core.serializers import TutorPayoutSerializer
import pytz
from datetime import timedelta, datetime
from core.extra_functions import getStartDateAndEndDateOfWeek
import requests
import json
import jwt
import smtplib
from core.sns import PublishTextMessage
from core.send_email import SendEmail
from core.ws import sendUpdate, sendBroadcast

@shared_task
def session_notifier():
    req_obs = Requests.objects.filter(status='accepted')
    timezone.activate(pytz.timezone("Asia/Manila"))

    for req_ob in req_obs:
        sess_ob = Session.objects.get(request=req_ob.id)
        timediff = sess_ob.start_date_time - timezone.localtime(timezone.now())
        minutediff = int(timediff.total_seconds() / 60)

        if minutediff == 30:
            tutor_message = "Session starting in 30 minutes with " + req_ob.child.first_name + ". Session link: " + sess_ob.meet_link
            parent_message = "Session starting in 30 minutes with " + sess_ob.tutor.first_name + ". Session link: " + sess_ob.meet_link
            subject = "Session starting in 30 minutes"
            # Push Notifications
            TutorNotification(tutor=sess_ob.tutor, is_seen=False, notification=tutor_message).save()
            ParentNotification(parent=req_ob.parent, is_seen=False, notification=parent_message).save()

            # Email Notifications
            SendEmail(subject, tutor_message, sess_ob.tutor.email)
            SendEmail(subject, parent_message, req_ob.parent.email)

            sendUpdate('tutor', 'update', sess_ob.tutor.id)
            sendUpdate('parent', 'update', req_ob.parent.id)

@shared_task
def chat_checker():
    chat_obs = Conversation.objects.filter(active=True, session__isnull=False)
    timezone.activate(pytz.timezone("Asia/Manila"))
    now = timezone.localtime(timezone.now())

    for chat_ob in chat_obs:
        end_time = chat_ob.session.end_date_time
        chat_validity = end_time + timedelta(hours=24)
        if now > chat_validity:
            chat_ob.active = False
            chat_ob.save()

@shared_task
def check_end_session():
    session_obs = Session.objects.filter(active='True')
    timezone.activate(pytz.timezone("Asia/Manila"))
    now = timezone.localtime(timezone.now())
    zoom_api_secret = 'Cli2AZfRrj8z7YCBnUlq3HzOhdtq0UQ7APgE'

    for session in session_obs:
        if now > session.end_date_time:
            request_id = session.request.id
            request_ob = Requests.objects.get(id=request_id)

            request_ob.status = 'finished'
            session.active = 'False'

            # sendUpdate('parent', 'update', request_ob.parent.id)
            # sendUpdate('tutor', 'update', session.tutor.id)
            # sendBroadcast("Session " + session.id + " has now ended")

            # END THE ZOOM MEETING
            # currentTime = int(datetime.now().timestamp())
            # token_data = {
            #     "aud": None,
            #     "iss": "P9xBzrKFSTmhu_Ca0EfP0w",
            #     "exp": currentTime + 3600,
            #     "iat": currentTime
            # }
            # access_token = jwt.encode(token_data, zoom_api_secret, algorithm='HS256').decode('utf8')
            #
            # url = "https://api.zoom.us/v2/meetings/" + session.zoom_id + "/status"
            # payload="{\"action\":\"end\"}"
            # headers = {
            # 'Authorization': 'Bearer '+access_token,
            # 'Content-Type': 'application/json',
            # }
            #
            # response = requests.request("PUT", url, headers=headers, data = payload)
            # print(response)

            session.save()
            request_ob.save()

            week_bracket = getStartDateAndEndDateOfWeek(str(session.end_date_time))
            tutor_payout = TutorPayout.objects.filter(tutor=session.tutor.id).filter(week_bracket=week_bracket)

            if tutor_payout.count() == 1:
                tutor_payout[0].session.add(session)
                tutor_payout[0].save()

            elif tutor_payout.count() == 0:
                session_list = []
                session_list.append(session.id)

                tutor_payout_data = {
                    "photo": "temp data",
                    "week_bracket": week_bracket,
                    "session": session_list,
                    "tutor": session.tutor.id,
                    "isPaid": False
                }

                tutor_payout_serializer_class = TutorPayoutSerializer(data=tutor_payout_data)
                if tutor_payout_serializer_class.is_valid():
                    tutor_payout_serializer_class.save()
                else:
                    # return print(tutor_payout_serializer_class.errors)
                    pass
