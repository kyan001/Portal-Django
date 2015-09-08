from django.conf.urls import include, url
from django.contrib import admin
from main import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    #USER
    url(r'^user/user', views.userUser),
    url(r'^user/profile/', views.userProfile),
    url(r'^user/avatar/(?P<email>[0-9a-zA-Z_.@]+)/$', views.userAvatar),
    url(r'^user/signin/$', views.userSignin),
    url(r'^user/signup/$', views.userSignup),
    url(r'^user/forgetanswer/$', views.userForgetanswer),
    url(r'^user/checklogin/$', views.userCheckLogin),
    url(r'^user/getloginerinfo/$', views.userGetloginerInfo),
    url(r'^user/newuser/$', views.userNewUser),
    url(r'^user/logout/$', views.userLogout),
    url(r'^user/validateusername$', views.userValidateUsername),
    url(r'^user/validatenickname$', views.userValidateNickname),
    url(r'^user/validateemail$', views.userValidateEmail),
    url(r'^user/getquestionandtip$', views.userGetQuestionAndTip),
    #PROGRESS
    url(r'^progress/list/$', views.progressList),
    url(r'^progress/detail$', views.progressDetail),
    url(r'^progress/fastupdate/$', views.progressFastupdate),
    url(r'^progress/new/$', views.progressNew),
    url(r'^progress/add/$', views.progressAdd),
    url(r'^progress/update/$', views.progressUpdate),
    url(r'^progress/delete/$', views.progressDelete),
    url(r'^progress/giveup/$', views.progressGiveup),
    url(r'^progress/reset/$', views.progressReset),
    url(r'^opus/mylist/$', views.opusMylist),
    url(r'^opus/detail$', views.opusDetail),
]
