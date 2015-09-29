from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Opus
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def opusDetail(request):
    '''TODO 获得作品的详情'''
    #获得参数
    opusid = request.GET.get('id')
    if not opusid:
        return infoMsg("需要一个作品id")
    #获得作品
    try:
        opus = Opus.objects.get(id=opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(opusid)))
    #render
    context = {}
    context['opus'] = opus
    return render_to_response('opus/detail.html', context)
