from django.shortcuts import render
from django.http import HttpResponse
from django.template import *

# Create your views here.
def index(request):
    return render_to_response("Hello");

def userIndex(request, username):
    context = {
        'content' : "你的用户名是：" + username,
        'title' : "用户名显示",
    }
    return render_to_response('msg.html', context);
