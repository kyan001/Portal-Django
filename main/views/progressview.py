from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Progress, Opus
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def getProgress(progressid):
    if not progressid:
        raise Exception("请输入进度信息 ID")
    try:
        opus = Opus.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度信息".format(str(progressid)))
    return opus

def progressList(request):
    context = {}
    user = getLoginUser();
    progresses = Progress.objects.filter(userid=user.id);
    progressList = []
    if not len(progresses):
        for p in progresses:
            opus = opusview.getOpus(p.opusid)
            l = {}
            l['name'] = opus.name
            l['subtitle'] = opus.subtitle
            l['total'] = opus.total
            l['current'] = p.current
            l['status'] = p.status
            l['modified'] = p.modified
            progressList.append(l)
    context['list'] = progressList
    return render_to_response('progress/list.html', context)
