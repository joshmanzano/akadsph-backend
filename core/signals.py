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
        AdminTutorMessage,
        AdminTutorConversation,
        AdminParentMessage,
        AdminParentConversation,
        TutorStrike
    )

from django.db.models.signals import post_save
import smtplib
from core.sns import PublishTextMessage
from core.send_email import SendEmail
from core.ws import sendUpdate, sendBroadcast
from multiprocessing import Process

def save_tutor_notification(sender, instance, created, **kwargs):
    if(created):
        if instance.status is "pending" and instance.is_favourite == False:
            subject_id = instance.subject.id
            subject_field = instance.subject.subject_field
            tutors = TutorSubject.objects.filter(subject=subject_id)
            parent_fname = instance.parent.first_name
            parent_lname = instance.parent.last_name

            tutor_emails = []
            subject = "Request Notification"
            message = "Tutorial Request with a " +subject_field + " subject has been made by " + parent_fname + "."

            for tutor in tutors:
                tutor_id = tutor.tutor
                # Push Notification
                TutorNotification(tutor=tutor_id, is_seen=False, notification=message).save()

                # Email Notification
                # SendEmail(subject, message, tutor.tutor.email)
                tutor_emails.append(tutor.tutor.email)

                # Text Notification
                # PublishTextMessage(tutor.tutor.phone, message)

                # Websocket alert
                sendUpdate('tutor', 'update', tutor.tutor.id)
                sendBroadcast(message)

            p = Process(target=SendEmail, args=(subject, message, tutor_emails))
            p.start()

        elif instance.status is "pending" and instance.is_favourite == True and instance.fav_tutor == None:
            fav_list = FavouriteTutor.objects.filter(parent=instance.parent.id)
            for fav in fav_list:
                tutor_ob = fav.tutor
                message = instance.parent.first_name + " has requested for your help in " +instance.subject.subject_field + "."
                subject = "Request Notification"
                # Push Notification
                TutorNotification(tutor=tutor_ob, is_seen=False, notification=message).save()

                # Email Notification
                p = Process(target=SendEmail, args=(subject, message, fav.tutor.email))
                p.start()
                # SendEmail(subject, message, fav.tutor.email)
                #
                # # Text Notification
                PublishTextMessage(fav.tutor.phone, message)

                # Websocket alert
                sendUpdate('tutor', 'update', fav.tutor.id)
                sendBroadcast(message)


        elif instance.status is "pending" and instance.is_favourite == True and instance.fav_tutor != None:
            message = instance.parent.first_name + " has requested for your help in " +instance.subject.subject_field + "."
            subject = "Request Notification"
            # Push Notification
            TutorNotification(tutor=instance.fav_tutor, is_seen=False, notification=message).save()

            # Email Notification
            p = Process(target=SendEmail, args=(subject, message, instance.fav_tutor.email))
            p.start()
            # SendEmail(subject, message, instance.fav_tutor.email)

            # # Text Notification
            PublishTextMessage(instance.fav_tutor.phone, message)

            # Websocket alert
            sendUpdate('tutor', 'update', instance.fav_tutor.id)
            sendBroadcast(message)

def save_parent_notification(sender, instance, created, **kwargs):
    if(created):
        if instance.active is "True":
            tutor_ob = Tutor.objects.get(id=instance.tutor.id)
            message = tutor_ob.first_name + " accepted your request!"
            subject = "Accepted Request Notification"
            # Push Notificatgion
            ParentNotification(parent=instance.request.parent, is_seen=False, notification=message).save()

            # Email Notification
            SendEmail(subject, message, instance.request.parent.email)
            #
            # # Text Notification
            PublishTextMessage(instance.request.parent.phone, message)

            # Websocket alert
            sendUpdate('parent', 'update', instance.request.parent.id)
            sendBroadcast(message)

def save_tutor_notification_accepted(sender, instance, created, **kwargs):
    if(created):
        if instance.active is "True" and instance.request.is_favourite == False:
            req_ob = Requests.objects.get(id=instance.request.id)
            declined_tutors = req_ob.declined_tutors.all()
            tutors = TutorSubject.objects.filter(subject=instance.request.subject.id)

            tutor_emails = []
            subject = "Request Notification"
            message = "Request made by " + instance.request.parent.first_name + " has been accepted by another tutor."

            for tutor in tutors:
                if tutor.tutor not in declined_tutors and tutor.tutor != instance.tutor:
                    TutorNotification(tutor=tutor.tutor, is_seen=False, notification=message).save()

                    # Email Notification
                    # SendEmail(subject, message, tutor.tutor.email)
                    tutor_emails.append(tutor.tutor.email)

                    # Text Notification
                    # PublishTextMessage(tutor.tutor.phone, message)

                    # Websocket alert
                    sendUpdate('tutor', 'update', tutor.tutor.id)
                    sendBroadcast(message)

            p = Process(target=SendEmail, args=(subject, message, tutor_emails))
            p.start()

def save_parent_notification_declined(sender, instance, created, **kwargs):
    if not (created):
        if instance.declined_tutors != None and instance.declined_reason != "" and instance.is_favourite == True:
            parent_id = instance.parent.id
            # tutor_ob = Tutor.objects.get(id=instance.tutor.id)
            tutor_list = ""
            if instance.declined_tutors.count() == 1:
                for dt in instance.declined_tutors.all():
                    tutor_list = dt.first_name + " " + dt.last_name
            else:
                for dt in instance.declined_tutors.all():
                    tutor_list = tutor_list + dt.first_name + ", "
            message = "The following tutors: " + tutor_list + " has/have declined your request because of the following reason: " + instance.declined_reason
            subject = "Declined Request"
            # Push Notification
            ParentNotification(parent=instance.parent, is_seen=False, notification=message).save()

            # Email Notification
            SendEmail(subject, message, instance.parent.email)

            # Text Notification
            PublishTextMessage(instance.parent.phone, message)

            # Websocket alert
            sendUpdate('parent', 'update', instance.parent.id)
            sendBroadcast(message)

            instance.declined_reason = ""
            instance.save()

def notify_conversation_user(sender, instance, created, **kwargs):
    if (created):
        sendUpdate('tutor', 'update', instance.conversation.tutor.id)
        sendUpdate('parent', 'update', instance.conversation.parent.id)

def notify_conversation_parent_admin(sender, instance, created, **kwargs):
    if (created):
        # sendUpdate('tutor', 'update', instance.conversation.tutor.id)
        sendUpdate('parent', 'update', instance.ap_conversation.parent.id)

def notify_conversation_tutor_admin(sender, instance, created, **kwargs):
    if (created):
        sendUpdate('tutor', 'update', instance.at_conversation.tutor.id)
        # sendUpdate('parent', 'update', instance.conversation.parent.id)

def notify_tutor_of_strikes(sender, instance, created, **kwargs):
    if (created):
        message = "Warning: your account has been striked for inappropriate conduct. Reason: " + instance.reason
        message2 = "Warning: your account has been striked for inappropriate conduct. Reason: \n" + instance.reason
        subject = "Strike Warning"
        TutorNotification(tutor=instance.tutor, is_seen=False, notification=message).save()
        # Email Notification
        SendEmail(subject, message2, instance.tutor.email)


post_save.connect(save_tutor_notification, sender=Requests)
post_save.connect(save_parent_notification, sender=Session)
post_save.connect(save_tutor_notification_accepted, sender=Session)
post_save.connect(save_parent_notification_declined, sender=Requests)
post_save.connect(notify_conversation_user, sender=Message)
post_save.connect(notify_conversation_parent_admin, sender=AdminParentMessage)
post_save.connect(notify_conversation_tutor_admin, sender=AdminTutorMessage)
post_save.connect(notify_tutor_of_strikes, sender=TutorStrike)
