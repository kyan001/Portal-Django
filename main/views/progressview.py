from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Progress, Opus
from django.core.cache import cache
import util.ctrl

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def progressList(request):
    context = {}
    #get user
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    #get user's progresses
    progresses = Progress.objects.filter(userid=user['id']).order_by('-modified');
    if len(progresses):
        #init vars
        pList = {}
        for st in Progress.status_pool.get('active'):
            pList[st] = [];
        #put progress items
        for prg in progresses:
            if prg.status in Progress.status_pool.get('active'):
                try:
                    opus = Opus.objects.get(id=prg.opusid)
                except Opus.DoesNotExist:
                    return infoMsg("未找到 id 为 {0} 的作品".format(str(p.opusid)))
                l = {}
                l['opus'] = opus
                l['prg'] = prg
                pList[prg.status].append(l)
        #put into context
        for st in Progress.status_pool.get('active'):
            if pList[st]:
                context['list'+st] = pList[st]
    return render_to_response('progress/list.html', context)

def progressArchive(request):
    context = {}
    #get user
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    #get user's progresses
    progresses = Progress.objects.filter(userid=user['id']).order_by('-modified');
    if len(progresses):
        #init vars
        pList = {}
        for st in Progress.status_pool.get('archive'):
            pList[st] = [];
        #put progress items
        for prg in progresses:
            if prg.status in Progress.status_pool.get('archive'):
                try:
                    opus = Opus.objects.get(id=prg.opusid)
                except Opus.DoesNotExist:
                    return infoMsg("未找到 id 为 {0} 的作品".format(str(p.opusid)))
                l = {}
                l['opus'] = opus
                l['prg'] = prg
                pList[prg.status].append(l)
        #put into context
        for st in Progress.status_pool.get('archive'):
            if pList[st]:
                context['list'+st] = pList[st]
    return render_to_response('progress/archive.html', context)

def progressDetail(request):
    context = {}
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
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
        return infoMsg("这个进度不属于您，因此您不能查看该进度", url='/progress/list')
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # calcs
    aux = {};
    if progress.current != 0 and opus.total != 0 and progress.status!='done':
        time_spend = progress.modified - progress.created
        estimate_finish_time = time_spend * (opus.total / progress.current)
        estimate_finish_date = progress.created + estimate_finish_time
        aux['estmt_fnsh_dt'] = util.ctrl.formatDate(estimate_finish_date, 'fulldateonly')
    # render
    context['opus'] = opus
    context['prg'] = progress
    context['aux'] = aux
    return render_to_response('progress/detail.html', context)

def progressImagecolor(request): #AJAX
    '''异步获取一个url的颜色'''
    url = request.GET.get('url')
    name = request.GET.get('name')
    if not name:
        return util.ctrl.returnJsonError('传入的 name 为空')
    cache_key = 'progress:' + name + ':imagecolor'
    cache_timeout = 60*60*24 # one day
    cached_color = cache.get(cache_key)
    result = {}
    if cached_color:
        result['is_cached'] = True;
        result['color'] = cached_color
    else:
        result['is_cached'] = False;
        if url:
            try:
                color = ktk.imageToColor(url, mode='hex')
                cache.set(cache_key, color, cache_timeout)
                result['color'] = color
            except Exception as e:
                return util.ctrl.returnJsonError(str(e))
    return util.ctrl.returnJson(result)

@csrf_exempt
def progressFastupdate(request):
    'detail界面右下角的快捷更新'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    quick_current = request.POST.get('quick_current')
    if quick_current == '':
        return util.ctrl.infoMsg("快速更新的当前进度不能为空" + quick_current, title="快速更新出错")
    quick_current = int(quick_current)
    if quick_current <= 0:
        quick_current = 0;
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # validation
    if opus.total > 0 and quick_current > opus.total:
        return util.ctrl.infoMsg("当前进度 {0} 超过最大值 {1}".format(str(quick_current), str(opus.total)))
    # save
    progress.current = quick_current;
    if(progress.setStatusAuto()):
        progress.setModified();
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressUpdate(request):
    'detail页面，编辑模式的保存'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    name = request.POST.get('name');
    subtitle = request.POST.get('subtitle');
    weblink = request.POST.get('weblink');
    total = request.POST.get('total');
    total = int(total) if total else 0;
    current = request.POST.get('current');
    current = int(current);
    if not name:
        return util.ctrl.infoMsg("名称（name）不能为空", title="保存失败")
    if not weblink:
        weblink = "";
    if current <= 0:
        current = 0;
    if total > 0 and current > total:
        return util.ctrl.infoMsg("初始进度 {0} 不能大于总页数 {1}".format(str(current), str(total)))
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
    # save
    progress.current = current;
    opus.name = name;
    opus.subtitle = subtitle;
    progress.weblink = weblink;
    opus.total = total;
    opus.save()
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressDelete(request):
    'detail 界面点击删除按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
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
        return util.ctrl.needLogin()
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
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
        return util.ctrl.needLogin()
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的进度".format(str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {0} 的作品".format(str(progress.opusid)))
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
        return util.ctrl.needLogin()
    # render
    return render_to_response('progress/new.html', context)

@csrf_exempt
def progressAdd(request):
    '新增界面点击保存按钮'
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    name = request.POST.get('name');
    subtitle = request.POST.get('subtitle');
    weblink = request.POST.get('weblink');
    if not weblink:
        weblink = "";
    total = request.POST.get('total');
    total = int(total) if total else 0;
    current = request.POST.get('current');
    current = int(current);
    tag1 = request.POST.get('tag1');
    tag2 = request.POST.get('tag2');
    tag3 = request.POST.get('tag3');
    tags = (tag1, tag2, tag3)
    if not name:
        return util.ctrl.infoMsg("名称（name）不能为空", title="保存失败")
    if current <= 0:
        current = 0;
    if total > 0 and current > total:
        return util.ctrl.infoMsg("初始进度 {0} 不能大于总页数 {1}".format(str(current), str(total)))
    opus = Opus(name=name, subtitle=subtitle, total=total)
    for t in tags:
        if(t):
            opus.addTag(t)
    opus.setCreated();
    opus.save()
    progress = Progress(current=current, opusid=opus.id, userid=user['id'], weblink=weblink)
    progress.setCreated();
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    progress.save()
    # render
    return redirect('/progress/list')
