from django.conf.urls import include, url
from django.contrib import admin
from main import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # INDEX
    url(r'^$', views.index, name='index'),
    url(r'^index/settheme$', views.indexSettheme),
    # USER
    url(r'^user/public$', views.userPublic),
    url(r'^user/profile/', views.userProfile),
    url(r'^user/exphistory$', views.userExphistory),
    url(r'^user/signin$', views.userSignin),  # get
    url(r'^user/signup$', views.userSignup),
    url(r'^user/headimgupdate$', views.userHeadimgUpdate),  # POST
    url(r'^user/forgetanswer/$', views.userForgetanswer),
    url(r'^user/forgetusername$', views.userForgetusername),  # POST
    url(r'^user/checklogin/$', views.userCheckLogin),  # POST
    url(r'^user/getunreadcount/$', views.userGetUnreadCount),
    url(r'^user/newuser/$', views.userNewUser),  # POST
    url(r'^user/logout/$', views.userLogout),
    url(r'^user/validateusername$', views.userValidateUsername),
    url(r'^user/validatenickname$', views.userValidateNickname),
    url(r'^user/validateemail$', views.userValidateEmail),
    url(r'^user/getquestionandtip$', views.userGetQuestionAndTip),
    url(r'^user/setting/$', views.userSetting),
    # PROGRESS
    url(r'^progress/list/$', views.progressList),
    url(r'^progress/archive/$', views.progressArchive),
    url(r'^progress/search$', views.progressSearch),  # get
    url(r'^progress/timeline$', views.progressTimeline),  # post
    url(r'^progress/detail$', views.progressDetail),  # get
    url(r'^progress/imagecolor$', views.progressImagecolor),  # get
    url(r'^progress/fastupdate/$', views.progressFastupdate),
    url(r'^progress/new/$', views.progressNew),
    url(r'^progress/add/$', views.progressAdd),
    url(r'^progress/update/$', views.progressUpdate),
    url(r'^progress/delete/$', views.progressDelete),
    url(r'^progress/giveup/$', views.progressGiveup),
    url(r'^progress/reset/$', views.progressReset),
    url(r'^progress/icalendar$', views.progressIcalendar),  # get
    url(r'^progress/setical$', views.progressSetical),  # post
    # OPUS
    url(r'^opus/detail$', views.opusDetail),
    url(r'^opus/searchopusinfo$', views.opusSearchOpusInfo),  # get Ajax
    # CHAT
    url(r'^chat/inbox$', views.chatInbox),
    url(r'^chat/markread$', views.chatMarkread),
    url(r'^chat/delete$', views.chatDelete),
    url(r'^chat/send$', views.chatSend),
    url(r'^chat/conversation$', views.chatConversation),
    # badge
    url(r'^badge/list/$', views.badgeList),
    url(r'^badge/detail$', views.badgeDetail),  # get
    # robo talk
    url(r'^robotalk$', views.robotalkIndex),
    url(r'^robotalk/getresponse$', views.robotalkGetresponse),  # get
    # SUPERUSER
    url(r'^superuser/index$', views.superuserIndex),
    url(r'^superuser/broadcast$', views.superuserBroadcast),
    url(r'^superuser/sendbroadcast$', views.superuserSendbroadcast),
    url(r'^superuser/updatedb$', views.superuserUpdatedb),
]
