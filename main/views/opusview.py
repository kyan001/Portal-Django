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
    context = {}
    #获得参数
    opusid = request.GET.get('id')
    if not opusid:
        return infoMsg("需要一个作品id")
    #获得作品
    try:
        opus = Opus.objects.get(id=opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(opusid)))
    #获得进度列表
    opus_list = Opus.objects.filter(name=opus.name)
    item_list = []
    for opuslet in opus_list:
        #获得进度
        try:
            progress = opuslet.getProgress()
        except Progress.DoesNotExist:
            return infoMsg("未找到 opusid 为 {0} 的进度".format(str(opusid)))
        #获得用户
        try:
            user = progress.getUser()
        except User.DoesNotExist:
            return infoMsg("未找到 id 为 {0} 的进度".format(str(progress.userid)))
        item_list.append({'progress':progress, 'user':user, 'opus':opuslet})
    #render
    context['opus'] = opus
    context['itemlist'] = item_list
    return render_to_response('opus/detail.html', context)
