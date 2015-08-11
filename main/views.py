from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import *
from main.models import *
import json

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
    return render_to_response('user/avatar.html', context)

def userUser(request):
    context = {}
    searchable_cols = ('username','id','email');
    try:
        for sc in searchable_cols:
            colname = sc if sc in request.GET else None
        if colname:
            kwargs = {colname : request.GET.get(colname)}
            user = User.objects.get(**kwargs);
        else:
            error_msg = "错误的参数：{0}\n".format(str(request.GET))
            error_msg += "请输入 {0} 中的一种".format(', '.join(searchable_cols))
            return infoMsg(error_msg, title='参数错误');
    except User.DoesNotExist:
        return infoMsg("用户 {0} 不存在".format(str(request.GET)), title='参数错误')
    context['headimg'] = user.getGravatar();
    context['user'] = user
    return render_to_response('user/index.html', context);
