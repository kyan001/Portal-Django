from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Progress, Opus
from util.ctrl import *
from . import userview

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def progressList(request):
    context = {}
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("请先登录！", url="/user/signin")
    progresses = Progress.objects.filter(userid=user['id']);
    progressList = []
    if len(progresses):
        for p in progresses:
            try:
                opus = Opus.objects.get(id=p.opusid)
            except Opus.DoesNotExist:
                return infoMsg("未找到 id 为 {0} 的作品".format(str(p.opusid)))
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
