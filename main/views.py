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

def userIndex(request, username):
    return infoMsg("您的用户名是：" + username)
