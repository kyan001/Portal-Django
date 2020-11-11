from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
import main.views.index
import main.views.user
import main.views.progress
import main.views.opus
import main.views.chat
import main.views.badge
import main.views.robotalk
import main.views.superuser
import main.views.tool


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
    url(r'^user/profile', main.views.user.profile),
    url(r'^user/exphistory$', main.views.user.exphistory),
    url(r'^user/signin$', main.views.user.signin),  # GET
    url(r'^user/signup$', main.views.user.signup),
    url(r'^user/headimgupdate$', main.views.user.headimgUpdate),  # POST
    url(r'^user/forgetanswer$', main.views.user.forgetAnswer),
    url(r'^user/forgetusername$', main.views.user.forgetUsername),  # POST
    url(r'^user/checklogin$', main.views.user.checkLogin),  # POST
    url(r'^user/getunreadcount$', main.views.user.getUnreadCount),
    url(r'^user/newuser$', main.views.user.newUser),  # POST
    url(r'^user/logout$', main.views.user.logout),
    url(r'^user/validateusername$', main.views.user.validateUsername),
    url(r'^user/validatenickname$', main.views.user.validateNickname),
    url(r'^user/validateemail$', main.views.user.validateEmail),
    url(r'^user/getquestionandtip$', main.views.user.getQuestionAndTip),
    url(r'^user/setting$', main.views.user.setting),
    # PROGRESS
    path('progress/service-worker.js', TemplateView.as_view(template_name='progress/service-worker.js', content_type='application/javascript')),  # PWA sw.js
    path('progress/manifest.json', TemplateView.as_view(template_name='progress/manifest.json', content_type='application/json')),  # PWA manifest.json
    path('progress/list', main.views.progress.list),
    path('progress/archive', main.views.progress.archive),
    path('progress/search', main.views.progress.search),  # GET
    path('progress/timeline', main.views.progress.timeline),  # POST
    path('progress/detail', main.views.progress.detail),  # GET
    path('progress/imagecolor', main.views.progress.imagecolor),  # GET
    path('progress/new', main.views.progress.new),  # GET
    path('progress/add', main.views.progress.add),  # POST
    path('progress/update', main.views.progress.update),  # POST
    path('progress/delete', main.views.progress.delete),  # POST
    path('progress/plusone', main.views.progress.plusone),  # GET
    path('progress/deactivate', main.views.progress.deactivate),  # POST
    path('progress/reactivate', main.views.progress.reactivate),  # POST
    path('progress/ical', main.views.progress.ical),  # GET
    path('progress/setsettings', main.views.progress.setsettings),  # POST
    path('progress/export', main.views.progress.export),  # GET
    # OPUS
    url(r'^opus/detail$', main.views.opus.detail),  # GET
    url(r'^opus/searchopusinfo$', main.views.opus.searchOpusInfo),  # GET Ajax
    url(r'^opus/getopuswordcloud$', main.views.opus.getOpusWordCloud),  # GET Ajax
    url(r'^opus/importfrom$', main.views.opus.importFrom),  # GET
    # CHAT
    url(r'^chat/inbox$', main.views.chat.inbox),
    url(r'^chat/markread$', main.views.chat.markread),
    url(r'^chat/delete$', main.views.chat.delete),
    url(r'^chat/send$', main.views.chat.send),
    url(r'^chat/conversation$', main.views.chat.conversation),
    # badge
    url(r'^badge/list$', main.views.badge.list),
    url(r'^badge/detail$', main.views.badge.detail),  # GET
    # robo talk
    url(r'^robotalk$', main.views.robotalk.index),
    url(r'^robotalk/getresponse$', main.views.robotalk.getResponse),  # GET
    # small tools
    path('tool/idvarify', main.views.tool.idVarify),  # GET Ajax
    # SUPERUSER
    url(r'^superuser/index$', main.views.superuser.index),
    url(r'^superuser/broadcast$', main.views.superuser.broadcast),
    url(r'^superuser/sendbroadcast$', main.views.superuser.sendbroadcast),
    url(r'^superuser/updatedb$', main.views.superuser.updatedb),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # add media folder as static files
