from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
import main.views.index
import main.views.user
import main.views.progress
import main.views.opus
import main.views.chat
import main.views.badge
import main.views.robotalk
import main.views.superuser


urlpatterns = [
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
    # I18N
    path('i18n/', include('django.conf.urls.i18n')),
    # INDEX
    url(r'^$', main.views.index.index, name='index'),
    url(r'^index/settheme$', main.views.index.settheme),
    url(r'^index/help$', main.views.index.help),
    # USER
    url(r'^user/public$', main.views.user.public),
    url(r'^user/profile/', main.views.user.profile),
    url(r'^user/exphistory$', main.views.user.exphistory),
    url(r'^user/signin$', main.views.user.signin),  # get
    url(r'^user/signup$', main.views.user.signup),
    url(r'^user/headimgupdate$', main.views.user.headimgUpdate),  # POST
    url(r'^user/forgetanswer/$', main.views.user.forgetAnswer),
    url(r'^user/forgetusername$', main.views.user.forgetUsername),  # POST
    url(r'^user/checklogin/$', main.views.user.checkLogin),  # POST
    url(r'^user/getunreadcount/$', main.views.user.getUnreadCount),
    url(r'^user/newuser/$', main.views.user.newUser),  # POST
    url(r'^user/logout/$', main.views.user.logout),
    url(r'^user/validateusername$', main.views.user.validateUsername),
    url(r'^user/validatenickname$', main.views.user.validateNickname),
    url(r'^user/validateemail$', main.views.user.validateEmail),
    url(r'^user/getquestionandtip$', main.views.user.getQuestionAndTip),
    url(r'^user/setting/$', main.views.user.setting),
    # PROGRESS
    url(r'^progress/list/$', main.views.progress.list),
    url(r'^progress/archive/$', main.views.progress.archive),
    url(r'^progress/search$', main.views.progress.search),  # get
    url(r'^progress/timeline$', main.views.progress.timeline),  # post
    url(r'^progress/detail$', main.views.progress.detail),  # get
    url(r'^progress/imagecolor$', main.views.progress.imagecolor),  # get
    url(r'^progress/new$', main.views.progress.new),  # get
    url(r'^progress/add/$', main.views.progress.add),
    url(r'^progress/update/$', main.views.progress.update),
    url(r'^progress/delete/$', main.views.progress.delete),
    url(r'^progress/giveup/$', main.views.progress.giveup),
    url(r'^progress/reset/$', main.views.progress.reset),
    url(r'^progress/ical$', main.views.progress.ical),  # get
    url(r'^progress/setical$', main.views.progress.setical),  # post
    # OPUS
    url(r'^opus/detail$', main.views.opus.detail),  # get
    url(r'^opus/searchopusinfo$', main.views.opus.searchOpusInfo),  # get Ajax
    url(r'^opus/getopuswordcloud$', main.views.opus.getOpusWordCloud),  # get Ajax
    url(r'^opus/importfrom$', main.views.opus.importFrom),  # get
    # CHAT
    url(r'^chat/inbox$', main.views.chat.inbox),
    url(r'^chat/markread$', main.views.chat.markread),
    url(r'^chat/delete$', main.views.chat.delete),
    url(r'^chat/send$', main.views.chat.send),
    url(r'^chat/conversation$', main.views.chat.conversation),
    # badge
    url(r'^badge/list/$', main.views.badge.list),
    url(r'^badge/detail$', main.views.badge.detail),  # get
    # robo talk
    url(r'^robotalk$', main.views.robotalk.index),
    url(r'^robotalk/getresponse$', main.views.robotalk.getResponse),  # get
    # SUPERUSER
    url(r'^superuser/index$', main.views.superuser.index),
    url(r'^superuser/broadcast$', main.views.superuser.broadcast),
    url(r'^superuser/sendbroadcast$', main.views.superuser.sendbroadcast),
    url(r'^superuser/updatedb$', main.views.superuser.updatedb),
    ]
