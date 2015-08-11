from django.shortcuts import render
from django.http import HttpResponse
from django.template import *

# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    return render_template("msg.html", context);

# Create your views here.
def index(request):
    return render_to_response("Hello");

def userIndex(request, username):
    return infoMsg("您的用户名是：" + username)
