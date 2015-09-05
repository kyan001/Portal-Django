from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Progress, Opus
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def progressList(request):
    context = {}
    #get user
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("请先登录！", url="/user/signin")
    #get user's progresses
    progresses = Progress.objects.filter(userid=user['id']);
    #init vars
    status_pool = ('done','inprogress','giveup','error')
    pList = {}
    for st in status_pool:
        pList[st] = [];
    if len(progresses):
        for prg in progresses:
            try:
                opus = Opus.objects.get(id=prg.opusid)
            except Opus.DoesNotExist:
                return infoMsg("未找到 id 为 {0} 的作品".format(str(p.opusid)))
            l = {}
            l['opus'] = opus
            l['prg'] = prg
            pList[prg.status].append(l)
    for st in status_pool:
        if pList[st]:
            context['list'+st] = pList[st]
    return render_to_response('progress/list.html', context)

def progressDetail(request):
    context = {}
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("请先登录！", url="/user/signin")
    progressid = request.GET.get('id')
    if not progressid:
        return infoMsg("请输入进度 ID")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNoteExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能查看该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # calcs

    # render
    context['opus'] = opus
    context['prg'] = progress
    return render_to_response('progress/detail.html', context)
