from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.template import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from main.models import *
from django.core.cache import cache
import util.ctrl

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def progressList(request):
    '''进度列表：显示所有进行中、待开始、追剧中的进度'''
    context = {'request': request}
    #get user
    loginuser = request.session.get('loginuser');
    if not loginuser:
        return util.ctrl.needLogin()
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return infoMsg("用户 id:{id} 不存在".format(id=str(loginuser['id'])), title='找不到用户')
    #get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified');
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
                    return infoMsg("未找到 id 为 {id} 的作品".format(id=str(p.opusid)))
                l = {}
                l['opus'] = opus
                l['prg'] = prg
                pList[prg.status].append(l)
        #put into context
        for st in Progress.status_pool.get('active'):
            if pList[st]:
                context['list'+st] = pList[st]
    else:
        chat_content = '''
            欢迎您使用「我的进度」<br/>
            请点击 “<a href="/progress/new">新建进度</a>” 按钮添加新的进度，<br/>
            “已完成”和“冻结中”的进度会存放在 <a href="/progress/archive">进度存档</a> 页面。<br/>
            最后，祝您使用愉快！
        '''
        Chat.objects.sendBySys(user, title='欢迎使用「我的进度」系统', content=chat_content)
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=loginuser['id'], category='progress')
    userexp.addExp(1, '访问进度列表页面')
    # render
    return render_to_response('progress/list.html', context)

def progressArchive(request):
    '''进度存档：显示所有已完成、已冻结的进度'''
    context = {'request': request}
    #get user
    loginuser = request.session.get('loginuser');
    if not loginuser:
        return util.ctrl.needLogin()
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return infoMsg("用户 id:{id} 不存在".format(id=str(loginuser['id'])), title='找不到用户')
    #get user's progresses
    progresses = Progress.objects.filter(userid=loginuser['id']).order_by('-modified');
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
                    return infoMsg("未找到 id 为 {id} 的作品".format(id=str(p.opusid)))
                l = {}
                l['opus'] = opus
                l['prg'] = prg
                pList[prg.status].append(l)
        #put into context
        for st in Progress.status_pool.get('archive'):
            if pList[st]:
                context['list'+st] = pList[st]
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=loginuser['id'], category='progress')
    userexp.addExp(1, '访问进度存档页面')
    # render
    return render_to_response('progress/archive.html', context)

def progressDetail(request):
    '''进度详情页'''
    context = {'request': request}
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
        return infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return infoMsg("这个进度不属于您，因此您不能查看该进度", url='/progress/list')
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(1, '查看进度《{opus.name}》的详情'.format(opus=opus))
    # calcs
    aux = {};
    if progress.status == 'done':
        time_spent = progress.modified - progress.created
        aux['time_spent'] = util.ctrl.formatTimedelta(time_spent)
    elif progress.current != 0 and opus.total != 0:
        time_spent_so_far = timezone.now() - progress.created
        estimate_finish_time = time_spent_so_far / progress.current * (opus.total - progress.current)
        if estimate_finish_time < datetime.timedelta(days=7):
            aux['estmt_fnsh_dt'] = util.ctrl.formatTimedelta(estimate_finish_time, '%d %H %M')
        else:
            estimate_finish_date = progress.created + estimate_finish_time
            aux['estmt_fnsh_dt'] = util.ctrl.formatDate(estimate_finish_date, 'fulldateonly')
    # render
    context['opus'] = opus
    context['prg'] = progress
    context['aux'] = aux
    return render_to_response('progress/detail.html', context)

def progressImagecolor(request): #AJAX #PUBLIC
    '''异步获取一个url的颜色'''
    url = request.GET.get('url')
    name = request.GET.get('name')
    result = {}
    if name:# has-name
        cache_key = 'progress:' + name.replace(' ','') + ':imagecolor'
        cache_timeout = 60*60*24*7*2 # 2 weeks
        cached_color = cache.get(cache_key)
        if cached_color: # has-name & cached
            result['is_cached'] = True;
            result['color'] = cached_color
            return util.ctrl.returnJson(result)
        else:# has-name & not-cached
            result['is_cached'] = False;
    if url: # no-name or not-cached
        try:
            color = ktk.imageToColor(url, mode='hex')
        except Exception as e:
            return util.ctrl.returnJsonError(str(e))
        result['color'] = color
        if name:
            cache.set(cache_key, color, cache_timeout)
    return util.ctrl.returnJson(result)


@csrf_exempt
def progressFastupdate(request):
    '''detail界面右下角的快捷更新'''
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
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {progress.opusid} 的作品".format(progress=progress))
    # validation
    if opus.total > 0 and quick_current > opus.total:
        return util.ctrl.infoMsg("当前进度 {quick_current} 超过最大值 {opus.total}".format(quick_current=quick_current, opus=opus))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '快捷更新进度《{opus.name}》'.format(opus=opus))
    # save
    progress.current = quick_current;
    if(progress.setStatusAuto()):
        progress.setModified();
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id={progress.id}'.format(progress=progress));

@csrf_exempt
def progressUpdate(request):
    '''detail页面，编辑模式的保存'''
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
        return util.ctrl.infoMsg("初始进度 {current} 不能大于总页数 {total}".format(current=current, total=total))
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '编辑进度《{opus.name}》成功'.format(opus=opus))
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
    return redirect('/progress/detail?id={progress.id}'.format(progress=progress));

@csrf_exempt
def progressDelete(request):
    '''detail 界面点击删除按钮'''
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
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '删除进度《{opus.name}》'.format(opus=opus))
    # save
    progress.delete()
    opus.delete()
    # render
    return redirect('/progress/list');

@csrf_exempt
def progressGiveup(request):
    '''detail 界面点击冻结按钮'''
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
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {progress.opusid} 的作品".format(progress=progress))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '冻结进度《{opus.name}》'.format(opus=opus))
    # save
    progress.setStatus('giveup')
    progress.save()
    # render
    return redirect('/progress/detail?id='+str(progress.id));

@csrf_exempt
def progressReset(request):
    '''detail 界面点击激活进度按钮'''
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
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user['id']:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {progress.opusid} 的作品".format(progress=progress))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '恢复已冻结的进度《{opus.name}》'.format(opus=opus))
    # save
    progress.resetStatus()
    progress.save()
    # render
    return redirect('/progress/detail?id='+str(progress.id));

def progressNew(request):
    '''list/detail 界面点击新增按钮'''
    context = {'request': request}
    # get inputs
    user = request.session.get('loginuser');
    if not user:
        return util.ctrl.needLogin()
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '尝试新增进度')
    # render
    return render_to_response('progress/new.html', context)

@csrf_exempt
def progressAdd(request):
    '''新增界面点击保存按钮'''
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
    if not name:
        return util.ctrl.infoMsg("名称（name）不能为空", title="保存失败")
    # validate
    if current <= 0:
        current = 0;
    if total > 0 and current > total:
        return util.ctrl.infoMsg("初始进度 {current} 不能大于总页数 {total}".format(current=current, total=total))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user['id'], category='progress')
    userexp.addExp(2, '新增进度《{name}》成功'.format(name=name))
    # save
    opus = Opus(name=name, subtitle=subtitle, total=total)
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
    return redirect('/progress/detail?id={progress.id}'.format(progress=progress))
