from django.urls import include, path
from rest_framework import routers
from core import views
from core.coreViews import (
    settingsViews,
    viewsetsViews,
    tutorsubjectViews,
    feedbackViews,
    notificationViews,
    chatViews,
    externalapiViews,
    requestViews,
    userViews,
    adminViews,
    trackerViews
)
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token

router = routers.DefaultRouter()
router.register(r'parents', viewsetsViews.ParentViewSet)
router.register(r'tutors', viewsetsViews.TutorViewSet)
router.register(r'requests', viewsetsViews.RequestsViewSet)
router.register(r'sessions', viewsetsViews.SessionViewSet)
router.register(r'children', viewsetsViews.ChildViewSet)
router.register(r'all-feedback', viewsetsViews.AllFeedbackViewSet)
router.register(r'feedback', viewsetsViews.FeedbackViewSet)
router.register(r'reports', viewsetsViews.ReportViewSet)
router.register(r'conversations', viewsetsViews.ConversationViewSet)
router.register(r'messages', viewsetsViews.MessageViewSet)
router.register(r'available-days', viewsetsViews.AvailableDaysViewSet)
router.register(r'favourite-tutors', viewsetsViews.FavouriteTutorViewSet)
router.register(r'paymongo-transactions', viewsetsViews.PayMongoTransactionViewSet)
router.register(r'subject', viewsetsViews.SubjectViewSet)
router.register(r'admin-setting', viewsetsViews.AdminSettingViewSet)
router.register(r'parent-setting', viewsetsViews.ParentSettingViewSet)
router.register(r'tutor-setting', viewsetsViews.TutorSettingViewSet)
router.register(r'parent-notification', viewsetsViews.ParentNotificationViewSet)
router.register(r'tutor-notification', viewsetsViews.TutorNotificationViewSet)
router.register(r'tutor-subject', viewsetsViews.TutorSubjectViewSet)
router.register(r'tutor-applications', viewsetsViews.TutorApplicationViewSet)
router.register(r'tutor-payouts', viewsetsViews.TutorPayoutViewSet)
router.register(r'general-promo', viewsetsViews.GeneralPromoViewset)
router.register(r'unique-promo', viewsetsViews.UniquePromoViewset)
router.register(r'shop-item', viewsetsViews.ShopItemViewSet)
router.register(r'admin', viewsetsViews.AdminViewset)
router.register(r'account-logger', viewsetsViews.AccountLoggerViewset)
router.register(r'admin-parent-conversation', viewsetsViews.AdminParentConversationViewset)
router.register(r'admin-parent-message', viewsetsViews.AdminParentMessageViewset)
router.register(r'admin-tutor-conversation', viewsetsViews.AdminTutorConversationViewset)
router.register(r'admin-tutor-message', viewsetsViews.AdminTutorMessageViewset)
router.register(r'tutor-strikes', viewsetsViews.TutorStrikeViewset)
router.register(r'credit-tracker', viewsetsViews.CreditTrackerViewset)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # ViewSets
    path('', include(router.urls)),

    # Settings
    path('update-parent-settings/', settingsViews.UpdateParentSettings.as_view()),
    path('update-tutor-settings/', settingsViews.UpdateTutorSettings.as_view()),
    path('get-parent-settings/', settingsViews.GetParentSettings.as_view()),
    path('get-tutor-settings/', settingsViews.GetTutorSettings.as_view()),

    # Subjects
    path('add-tutor-subject/', tutorsubjectViews.AddTutorSubjects.as_view()),
    path('delete-tutor-subject/', tutorsubjectViews.DeleteTutorSubjects.as_view()),

    # Feedback
    path('parent-report/', feedbackViews.ParentReport.as_view()),
    path('tutor-report/', feedbackViews.TutorReport.as_view()),
    path('parent-feedback/', feedbackViews.ParentFeedback.as_view()),
    path('tutor-feedback/', feedbackViews.TutorFeedback.as_view()),

    # Notifications
    path('tutor-recent-notifications/', notificationViews.GetTutorNotifications.as_view()),
    path('parent-recent-notifications/', notificationViews.GetParentNotifications.as_view()),
    path('seen-all-tutor-notifications/', notificationViews.SeenAllTutorNotifications.as_view()),
    path('seen-all-parent-notifications/', notificationViews.SeenAllParentNotifications.as_view()),

    # Chat
    path('tutor-chats/', chatViews.TutorChats.as_view()),
    path('parent-chats/', chatViews.ParentChats.as_view()),
    path('specific-conversation/', chatViews.SpecificConversation.as_view()),
    path('get-unseen-specific-conversation/', chatViews.GetUnseenFromSpecificConversation.as_view()),
    path('send-message/', chatViews.SendMessage.as_view()),
    path('seen-conversation/', chatViews.SeenConversation.as_view()),

    # Chat: Admin-Tutor
    path('specific-tutor-admin-conversation/', chatViews.SpecificAdminTutorConversation.as_view()),
    path('get-unseen-specific-tutor-admin-conversation/', chatViews.GetUnseenFromSpecificAdminTutorConversation.as_view()),
    path('send-admin-tutor-message/', chatViews.SendAdminTutorMessage.as_view()),
    path('seen-admin-tutor-conversation/', chatViews.SeenAdminTutorConversation.as_view()),

    # Chat: Admin-Parent
    path('specific-parent-admin-conversation/', chatViews.SpecificAdminParentConversation.as_view()),
    path('get-unseen-specific-parent-admin-conversation/', chatViews.GetUnseenFromSpecificAdminParentConversation.as_view()),
    path('send-admin-parent-message/', chatViews.SendAdminParentMessage.as_view()),
    path('seen-admin-parent-conversation/', chatViews.SeenAdminParentConversation.as_view()),

    # Request
    path('find-available-days-request/', requestViews.FindAvailableDaysRequest.as_view()),
    path('specific-request/', requestViews.SpecificRequest.as_view()),
    path('parent-cancel-session/', requestViews.CancelSession.as_view()),
    path('tutor-cancel-session/', requestViews.TutorCancelSession.as_view()),
    path('end-session/', requestViews.EndSession.as_view()),
    path('parent-cancel-request/', requestViews.ParentCancelRequest.as_view()),
    path('tutor-decline-request/', requestViews.TutorDeclineRequest.as_view()),
    path('extend-session/', requestViews.ExtendSession.as_view()),

    # Users
    path('all-parent-details/', userViews.AllParentDetails.as_view()),
    path('specific-tutor/', userViews.SpecificTutorView.as_view()),
    path('all-tutor-details/', userViews.AllTutorDetails.as_view()),
    path('tutor-payout/', userViews.TutorPayoutAPI.as_view()),
    path('add-favourite-tutor/', userViews.AddFavouriteTutor.as_view()),
    path('parent-make-request/', userViews.ParentMakeRequest.as_view()),
    path('tutor-accept-request/', userViews.TutorAcceptRequest.as_view()),
    path('all-parent-transactions/', userViews.AllParentTransactions.as_view()),
    path('make-tutor-application/', userViews.MakeTutorApplication.as_view()),
    path('parent-non-first-time/', userViews.ParentNotFirstTimeUser.as_view()),
    path('tutor-non-first-time/', userViews.TutorNotFirstTimeUser.as_view()),
    path('add-children/', userViews.AddChild.as_view()),

    # Admin
    path('tutor-application-to-tutor-object/', adminViews.TutorApplicationToTutorObject.as_view()),
    path('all-admin-details/', adminViews.AllAdminDetails.as_view()),
    path('upload-receipt/', adminViews.UploadReceiptForPayout.as_view()),
    path('create-gen-promo/', adminViews.CreateGeneralPromoCode.as_view()),
    path('create-uni-promo/', adminViews.CreateUniquePromoCode.as_view()),
    path('disable-parent/', adminViews.DisableParent.as_view()),
    path('disable-tutor/', adminViews.DisableTutor.as_view()),
    path('email-tutors/', adminViews.EmailTutors.as_view()),
    path('enable-parent/', adminViews.EnableParent.as_view()),
    path('enable-tutor/', adminViews.EnableTutor.as_view()),
    path('login-as/', views.LoginAs.as_view()),
    path('add-shop-item/', adminViews.CreateShopItem.as_view()),
    path('archive-shop-item/', adminViews.ArchiveShopItem.as_view()),
    path('add-credit/', trackerViews.AddCreditToParent.as_view()),
    path('subtract-credit/', trackerViews.SubtractCreditToParent.as_view()),

    # TO DEPRECIATE
    path('add-credits/', views.AddCredits.as_view()),
    path('approve-tutor/', views.ApproveTutor.as_view()),
    path('find-pending-requests/', views.FindPendingRequests.as_view()),
    path('find-accepted-requests-and-sessions-parent-date/', views.FindAcceptedRequestsAndSessionsParentDate.as_view()),
    path('find-accepted-requests-and-sessions-tutor-date/', views.FindAcceptedRequestsAndSessionsTutorDate.as_view()),
    path('find-finished-requests-user', views.FindFinishedRequestsUser.as_view()),
    path('find-pending-requests-user', views.FindPendingRequestsUser.as_view()),
    path('parent-requests/<int:pk>/', views.ParentRequests.as_view()),
    path('pending-tutors/', views.PendingTutors.as_view()),
    path('tutor-requests/<email>/', views.TutorRequests.as_view()),
    path('specific-parent-username/', views.SpecificParentUsername.as_view()),
    path('update-parent/<int:pk>/', views.UpdateParent.as_view()),
    path('update-tutor/<int:pk>/', views.UpdateTutor.as_view()),
    path('parent-all-finished-sessions/', views.AllParentsFinishedSessions.as_view()),
    path('tutor-all-finished-sessions/', views.AllTutorsFinishedSessions.as_view()),
    path('delete-feedback/<int:pk>/', views.DeleteFeedbackView.as_view()),
    path('delete-child/<int:pk>/', views.DeleteChildView.as_view()),
    path('delete-parent/<int:pk>/', views.DeleteParentView.as_view()),
    path('delete-tutor/<int:pk>/', views.DeleteTutorView.as_view()),
    path('purge-users/', views.PurgeUserView.as_view()),

    # EXTERNAL/Authentication endpoints
    path('login-parent/', views.LoginParent.as_view()),
    path('register-parent/', views.RegisterParent.as_view()),
    path('register-admin/', views.RegisterAdmin.as_view()),
    path('register-tutor/', views.RegisterTutor.as_view()),
    path('login-tutor/', views.LoginTutor.as_view()),
    path('receive-tutor-email/', views.ReceiveTutorEmail.as_view()),
    path('tokeninfo/', views.TokenInfo.as_view()),
	path('zoom/', views.ZoomAPI.as_view()),
	path('paymongo/', views.PayMongoAPI.as_view()),
	path('brankas/', views.BrankasAPI.as_view()),
	path('verify-brankas/', views.VerifyBrankasAPI.as_view()),
	path('source-paymongo/', views.SourcePayMongoAPI.as_view()),
	path('verify-source-paymongo/', views.VerifySourcePayMongoAPI.as_view()),
	path('verify-paymongo/', views.VerifyPayMongoAPI.as_view()),
    path('twilio/', views.TwilioAPI.as_view()),
    path('email/', views.EmailAPI.as_view()),
    path('brankas/', views.BrankasAPI.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-verify/', verify_jwt_token),
    path('database-check/', views.database_check),
    path('health-check/', include('health_check.urls'))

]
