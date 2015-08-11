from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import *
from main.models import *

# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    return render_to_response("msg.html", context);

# Create your views here.
def index(request):
    return render_to_response('index/index.html');

def userAvatar(request, email):
    context = {}
    if email:
        user = User(email=email)
        context['headimg'] = user.getGravatar()
    else:
        return infoMsg("请输入email")
    return render_to_response('<img src="{{headimg}}">', context)

def userUser(request, keyword):
    context = {}
    searchable_cols = ('username','id','email');
    for sc in searchable_cols:
        kwargs = {sc:keyword}
        queryset = User.objects.filter(**kwargs);
        if len(queryset)==1:
            user = queryset[0];
            break;
    if not user:
        return infoMsg("无法找到用户 " + keyword + " 不存在！")
    context['headimg'] = user.getGravatar();
    context['user'] = user
    return render_to_response('user/index.html', context);
