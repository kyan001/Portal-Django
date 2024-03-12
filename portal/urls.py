from django.urls import include, path
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
    # path('', 'portal.views.home', name='home'),
    # path('blog/', include('blog.urls')),

    path('admin/', admin.site.urls),
    # I18N
    path('i18n/', include('django.conf.urls.i18n')),
    # INDEX
    path('', main.views.index.index, name='index'),
    path('index/settheme', main.views.index.settheme),
    path('index/help', main.views.index.help),
    # USER
    path('user/public', main.views.user.public),
    path('user/profile', main.views.user.profile),
    path('user/exphistory', main.views.user.exphistory),
    path('user/signin', main.views.user.signin),  # GET
    path('user/signup', main.views.user.signup),
    path('user/headimgupdate', main.views.user.headimgUpdate),  # POST
    path('user/forgetanswer', main.views.user.forgetAnswer),
    path('user/forgetusername', main.views.user.forgetUsername),  # POST
    path('user/checklogin', main.views.user.checkLogin),  # POST
    path('user/getunreadcount', main.views.user.getUnreadCount),
    path('user/newuser', main.views.user.newUser),  # POST
    path('user/logout', main.views.user.logout),
    path('user/validateusername', main.views.user.validateUsername),
    path('user/validatenickname', main.views.user.validateNickname),
    path('user/validateemail', main.views.user.validateEmail),
    path('user/getquestionandtip', main.views.user.getQuestionAndTip),
    path('user/setting', main.views.user.setting),
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
    path('opus/detail', main.views.opus.detail),  # GET
    path('opus/searchopusinfo', main.views.opus.searchOpusInfo),  # GET Ajax
    path('opus/getopuswordcloud', main.views.opus.getOpusWordCloud),  # GET Ajax
    path('opus/importfrom', main.views.opus.importFrom),  # GET
    # CHAT
    path('chat/inbox', main.views.chat.inbox),
    path('chat/markread', main.views.chat.markread),
    path('chat/delete', main.views.chat.delete),
    path('chat/send', main.views.chat.send),
    path('chat/conversation', main.views.chat.conversation),
    # badge
    path('badge/list', main.views.badge.list),
    path('badge/detail', main.views.badge.detail),  # GET
    # robo talk
    path('robotalk', main.views.robotalk.index),
    path('robotalk/getresponse', main.views.robotalk.getResponse),  # GET
    # small tools
    path('tool/idvarify', main.views.tool.idVarify),  # GET Ajax
    # SUPERUSER
    path('superuser/index', main.views.superuser.index),
    path('superuser/broadcast', main.views.superuser.broadcast),
    path('superuser/sendbroadcast', main.views.superuser.sendbroadcast),
    path('superuser/updatedb', main.views.superuser.updatedb),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # add media folder as static files
