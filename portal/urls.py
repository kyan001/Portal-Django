from django.conf.urls import include, url
from django.contrib import admin
from main import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # INDEX
    url(r'^$', views.indexview.index, name='index'),
    url(r'^index/settheme$', views.indexview.indexSettheme),
    url(r'^index/help$', views.indexview.indexHelp),
    # USER
    url(r'^user/public$', views.userview.userPublic),
    url(r'^user/profile/', views.userview.userProfile),
    url(r'^user/exphistory$', views.userview.userExphistory),
    url(r'^user/signin$', views.userview.userSignin),  # get
    url(r'^user/signup$', views.userview.userSignup),
    url(r'^user/headimgupdate$', views.userview.userHeadimgUpdate),  # POST
    url(r'^user/forgetanswer/$', views.userview.userForgetanswer),
    url(r'^user/forgetusername$', views.userview.userForgetusername),  # POST
    url(r'^user/checklogin/$', views.userview.userCheckLogin),  # POST
    url(r'^user/getunreadcount/$', views.userview.userGetUnreadCount),
    url(r'^user/newuser/$', views.userview.userNewUser),  # POST
    url(r'^user/logout/$', views.userview.userLogout),
    url(r'^user/validateusername$', views.userview.userValidateUsername),
    url(r'^user/validatenickname$', views.userview.userValidateNickname),
    url(r'^user/validateemail$', views.userview.userValidateEmail),
    url(r'^user/getquestionandtip$', views.userview.userGetQuestionAndTip),
    url(r'^user/setting/$', views.userview.userSetting),
    # PROGRESS
    url(r'^progress/list/$', views.progressview.progressList),
    url(r'^progress/archive/$', views.progressview.progressArchive),
    url(r'^progress/search$', views.progressview.progressSearch),  # get
    url(r'^progress/timeline$', views.progressview.progressTimeline),  # post
    url(r'^progress/detail$', views.progressview.progressDetail),  # get
    url(r'^progress/imagecolor$', views.progressview.progressImagecolor),  # get
    url(r'^progress/fastupdate/$', views.progressview.progressFastupdate),
    url(r'^progress/new/$', views.progressview.progressNew),
    url(r'^progress/add/$', views.progressview.progressAdd),
    url(r'^progress/update/$', views.progressview.progressUpdate),
    url(r'^progress/delete/$', views.progressview.progressDelete),
    url(r'^progress/giveup/$', views.progressview.progressGiveup),
    url(r'^progress/reset/$', views.progressview.progressReset),
    url(r'^progress/icalendar$', views.progressview.progressIcalendar),  # get
    url(r'^progress/setical$', views.progressview.progressSetical),  # post
    # OPUS
    url(r'^opus/detail$', views.opusview.opusDetail),
    url(r'^opus/searchopusinfo$', views.opusview.opusSearchOpusInfo),  # get Ajax
    # CHAT
    url(r'^chat/inbox$', views.chatview.chatInbox),
    url(r'^chat/markread$', views.chatview.chatMarkread),
    url(r'^chat/delete$', views.chatview.chatDelete),
    url(r'^chat/send$', views.chatview.chatSend),
    url(r'^chat/conversation$', views.chatview.chatConversation),
    # badge
    url(r'^badge/list/$', views.badgeview.badgeList),
    url(r'^badge/detail$', views.badgeview.badgeDetail),  # get
    # robo talk
    url(r'^robotalk$', views.robotalkview.robotalkIndex),
    url(r'^robotalk/getresponse$', views.robotalkview.robotalkGetresponse),  # get
    # SUPERUSER
    url(r'^superuser/index$', views.superuserview.superuserIndex),
    url(r'^superuser/broadcast$', views.superuserview.superuserBroadcast),
    url(r'^superuser/sendbroadcast$', views.superuserview.superuserSendbroadcast),
    url(r'^superuser/updatedb$', views.superuserview.superuserUpdatedb),
]
