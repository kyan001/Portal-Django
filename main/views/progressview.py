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
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
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
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.GET.get('id')
    if not progressid:
        return infoMsg("请输入进度 ID")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
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

@csrf_exempt
def progressFastupdate(request):
    'detail界面右下角的快捷更新'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.POST.get('id')
    if not progressid:
        return infoMsg("进度 ID 为空，请联系管理员", title="出错")
    newcurrent = request.POST.get('newcurrent')
    newcurrent = int(newcurrent)
    if newcurrent <= 0:
        newcurrent = 0;
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # validation
    if newcurrent > opus.total:
        return infoMsg("当前进度 {0} 超过最大值 {1}".format(str(newcurrent), str(opus.total)))
    # save
    progress.current = newcurrent;
    if(progress.setStatusAuto()):
        progress.setModified();
        progress.save()
    else:
        return infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressUpdate(request):
    'detail页面，编辑模式的保存'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.POST.get('id')
    if not progressid:
        return infoMsg("进度 ID 为空，请联系管理员", title="出错")
    name = request.POST.get('name');
    subtitle = request.POST.get('subtitle');
    total = request.POST.get('total');
    total = int(total);
    current = request.POST.get('current');
    current = int(current);
    if not name:
        return infoMsg("名称（name）不能为空", title="保存失败")
    if not total:
        return infoMsg("总页数（total）不能为空或 0", title="保存失败")
    if current <= 0:
        current = 0;
    if current > total:
        return infoMsg("初始进度 {0} 不能大于总页数 {1}".format(str(current), str(total)))
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # save
    progress.current = current;
    opus.name = name;
    opus.subtitle = subtitle;
    opus.total = total;
    opus.save()
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressDelete(request):
    'detail 界面点击删除按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.POST.get('id')
    if not progressid:
        return infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # save
    progress.delete()
    opus.delete()
    # render
    return redirect('/progress/list');

@csrf_exempt
def progressGiveup(request):
    'detail 界面点击放弃按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.POST.get('id')
    if not progressid:
        return infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # save
    progress.setStatus('giveup')
    progress.save()
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressReset(request):
    'detail 界面点击取消弃置按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    progressid = request.POST.get('id')
    if not progressid:
        return infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # save
    progress.resetStatus()
    progress.save()
    # render
    return redirect('/progress/detail?id='+str(progress.id));

def progressNew(request):
    'list/detail 界面点击新增按钮'
    context = {}
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    # render
    return render_to_response('progress/new.html', context)

@csrf_exempt
def progressAdd(request):
    '新增界面点击保存按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    name = request.POST.get('name');
    subtitle = request.POST.get('subtitle');
    total = request.POST.get('total');
    total = int(total);
    current = request.POST.get('current');
    current = int(current);
    tag1 = request.POST.get('tag1');
    tag2 = request.POST.get('tag2');
    tag3 = request.POST.get('tag3');
    tags = (tag1, tag2, tag3)
    if not name:
        return infoMsg("名称（name）不能为空", title="保存失败")
    if not total:
        return infoMsg("总页数（total）不能为空或 0", title="保存失败")
    if current <= 0:
        current = 0;
    if current > total:
        return infoMsg("初始进度 {0} 不能大于总页数 {1}".format(str(current), str(total)))
    opus = Opus(name=name, subtitle=subtitle, total=total)
    for t in tags:
        if(t):
            opus.addTag(t)
    opus.setCreated();
    opus.save()
    progress = Progress(current=current, opusid=opus.id, userid=user['id'])
    progress.setCreated();
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    progress.save()
    # render
    return redirect('/progress/list')
