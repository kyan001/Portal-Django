from django.conf.urls import include, url
from django.contrib import admin
from main import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'portal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^user/(?P<username>[a-zA-Z0-9_]+)/$', views.userIndex)
]
