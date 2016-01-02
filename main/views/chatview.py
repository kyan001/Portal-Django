from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
#from main.models import Chat
from django.core.cache import cache
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def chatInbox(request):
    '''用户查看自己的 inbox'''
    context = {}
    return render_to_response('chat/inbox.html', context)
