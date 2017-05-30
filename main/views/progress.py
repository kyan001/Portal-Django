from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from main.models import User, UserExp, Opus, Progress, Chat
from django.db.models import Q
from django.core.cache import cache
import icalendar
import util.ctrl
import util.time
import util.user

import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


def list(request):
    '''进度列表：显示所有进行中、待开始、追剧中的进度'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st in Progress.STATUS_ROLE.get('active'):
            prg_list[st] = progresses.filter(status=st)
    else:
        if not user.getChats('received').filter(senderid=Chat.objects.getSyschatUser().id, title='欢迎使用「我的进度」系统').exists():
            chat_content = '''
欢迎您使用「我的进度」<br/>
请点击 “<a href="/progress/new">新建进度</a>” 按钮添加新的进度，<br/>
“已完成”和“冻结中”的进度会存放在 <a href="/progress/archive">进度存档</a> 页面。<br/>
最后，祝您使用愉快！
            '''
            Chat.objects.sendBySys(user, title='欢迎使用「我的进度」系统', content=chat_content)
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(1, '访问「进度列表」页面')
    # render
    context = {
        'prglist': prg_list,
        }
    return render(request, 'progress/list.html', context)


def archive(request):
    '''进度存档：显示所有已完成、已冻结的进度'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st in Progress.STATUS_ROLE.get('archive'):
            prg_list[st] = progresses.filter(status=st)
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(1, '访问「进度存档」页面')
    # render
    context = {
        'prglist': prg_list,
    }
    return render(request, 'progress/archive.html', context)


def search(request):
    '''进度搜索：筛选所有进度'''
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('created')
    context['prglist'] = progresses
    # pass searched keyword
    keyword = request.GET.get('kw') or ""
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(1, '访问「进度搜索」页面')
    # render
    context = {
        'prglist': progresses,
        'keyword': keyword,
    }
    return render(request, 'progress/search.html', context)


def timeline(request):
    '''进度历程：显示所有进度的时间轴'''
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    # add timeline info
    now_year = timezone.now().year
    context['prg_timeline_this_year'] = progresses.filter(Q(created__year=now_year) | Q(modified__year=now_year))  # created or modified in this year
    last_year = timezone.now().year - 1
    context['prg_timeline_last_year'] = progresses.filter(Q(created__year=last_year) | Q(modified__year=last_year))  # created or modified in this year
    context['prglist'] = progresses
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(1, '访问「进度列表」页面')
    # render
    return render(request, 'progress/timeline.html', context)


def detail(request):
    '''进度详情页'''
    context = {}
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    progressid = request.GET.get('id')
    if not progressid:
        return util.ctrl.infoMsg("请输入进度 ID")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user.id:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能查看该进度", url='/progress/list')
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(1, '查看进度《{opus.name}》的详情'.format(opus=opus))
    # calcs
    aux = {
        'time': {},
        'esti': {},
    }
    aux['time']['c2n'] = util.time.formatDateToNow(progress.created, 'largest')
    aux['time']['m2n'] = util.time.formatDateToNow(progress.modified, 'largest')
    aux['time']['c2m'] = util.time.formatTimedelta(progress.getTimedelta('c2m'))
    if opus.total and progress.current:  # 非追剧中、非待开始有预计完成时间
        esti_finish_timedelta = progress.getTimedelta('c2n') / progress.current * (opus.total - progress.current)
        esti_finish_date = progress.modified + esti_finish_timedelta
        aux['esti']['finish_date'] = esti_finish_date
        aux['esti']['finish_time'] = util.time.formatDateToNow(esti_finish_date, 'largest')
    if progress.current:  # 平均阅读速度
        speed = progress.getTimedelta('speed')
        if speed:
            aux['time']['speed'] = util.time.formatTimedelta(speed)
    # render
    context['opus'] = opus
    context['prg'] = progress
    context['aux'] = aux
    return render(request, 'progress/detail.html', context)


def imagecolor(request):  # AJAX #PUBLIC
    '''异步获取一个url的颜色'''
    url = request.GET.get('url')
    opusid = request.GET.get('opusid')
    result = {}
    if opusid:  # has-opusid
        cache_key = 'opus:{}:covercolor'.format(opusid)
        cache_timeout = 60 * 60 * 24 * 7 * 2  # 2 weeks
        cached_color = cache.get(cache_key)
        if cached_color:  # has-opusid & cached
            result['is_cached'] = True
            result['color'] = cached_color
            return util.ctrl.returnJson(result)
        else:  # has-opusid & not-cached
            result['is_cached'] = False
    if url:  # no-opusid or not-cached
        try:
            color = ktk.imageToColor(url, mode='hex')
        except Exception as e:
            return util.ctrl.returnJsonError(str(e))
        result['color'] = color
        if opusid:
            cache.set(cache_key, color, cache_timeout)
    return util.ctrl.returnJson(result)


def update(request):
    '''detail页面，编辑模式的保存'''
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    name = request.POST.get('name')
    subtitle = request.POST.get('subtitle')
    weblink = request.POST.get('weblink')
    total = request.POST.get('total')
    total = int(total) if total else 0
    current = request.POST.get('current')
    current = int(current)
    if not name:
        return util.ctrl.infoMsg("名称（name）不能为空", title="保存失败")
    if not weblink:
        weblink = ""
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return util.ctrl.infoMsg("初始进度 {current} 不能大于总页数 {total}".format(current=current, total=total))
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user.id:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能更新该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '编辑进度《{opus.name}》成功'.format(opus=opus))
    # save
    progress.current = current
    opus.name = name
    opus.subtitle = subtitle
    progress.weblink = weblink
    opus.total = total
    opus.save()
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    # render
    return redirect('/progress/detail?id={progress.id}'.format(progress=progress))


def delete(request):
    '''detail 界面点击删除按钮'''
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user.id:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(progress.opusid)))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '删除进度《{opus.name}》'.format(opus=opus))
    # save
    progress.delete()
    opus.delete()
    # render
    return redirect('/progress/list')


def giveup(request):
    '''detail 界面点击冻结按钮'''
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user.id:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {progress.opusid} 的作品".format(progress=progress))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '冻结进度《{opus.name}》'.format(opus=opus))
    # save
    progress.status = 'giveup'
    progress.save()
    # render
    return redirect('/progress/detail?id=' + str(progress.id))


def reset(request):
    '''detail 界面点击激活进度按钮'''
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    progressid = request.POST.get('id')
    if not progressid:
        return util.ctrl.infoMsg("进度 ID 为空，请联系管理员", title="出错")
    # get progress
    try:
        progress = Progress.objects.get(id=progressid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的进度".format(id=str(progressid)))
    # check owner
    if progress.userid != user.id:
        return util.ctrl.infoMsg("这个进度不属于您，因此您不能删除该进度")
    # get opus
    try:
        opus = Opus.objects.get(id=progress.opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {progress.opusid} 的作品".format(progress=progress))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '恢复已冻结的进度《{opus.name}》'.format(opus=opus))
    # save
    progress.resetStatus()
    progress.save()
    # render
    return redirect('/progress/detail?id=' + str(progress.id))


def new(request):
    '''list/detail 界面点击新增按钮'''
    context = {}
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '尝试新增进度')
    # render
    return render(request, 'progress/new.html', context)


def add(request):
    '''新增界面点击保存按钮'''
    # get inputs
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    name = request.POST.get('name')
    subtitle = request.POST.get('subtitle')
    weblink = request.POST.get('weblink')
    if not weblink:
        weblink = ""
    total = request.POST.get('total')
    total = int(total) if total else 0
    current = request.POST.get('current')
    current = int(current)
    if not name:
        return util.ctrl.infoMsg("名称（name）不能为空", title="保存失败")
    # validate
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return util.ctrl.infoMsg("初始进度 {current} 不能大于总页数 {total}".format(current=current, total=total))
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='progress')
    userexp.addExp(2, '新增进度《{name}》成功'.format(name=name))
    # save
    opus = Opus(name=name, subtitle=subtitle, total=total)
    opus.save()
    progress = Progress(current=current, opusid=opus.id, userid=user.id, weblink=weblink)
    if(progress.setStatusAuto()):
        progress.save()
    else:
        return util.ctrl.infoMsg("储存进度时失败，可能是状态导致的问题", title="存储 progress 出错")
    progress.save()
    # render
    return redirect('/progress/detail?id={progress.id}'.format(progress=progress))


def setical(request):  # POST
    '''用户设置进度日历的界面'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    use_ical = request.POST.get('useical') or 'off'
    icalon = (use_ical == 'on')
    user.setUserpermission('progressical', icalon)
    return redirect('/user/setting')


def ical(request):  # GET
    '''生成 ical 字符串加入 google calendar'''
    userid = request.GET.get('userid')
    privatekey = request.GET.get('private') or None
    try:
        user = User.objects.get(id=userid)
    except User.DoesNotExist:
        return util.ctrl.infoMsg("用户 userid={id} 不存在".format(id=userid), title='找不到用户')
    if privatekey:  # private mode
        if privatekey != user.privatekey:
            return util.ctrl.infoMsg("用户的私钥不合法", title='无法读取')
    else:  # public mode
        if not user.getUserpermission('progressical'):
            return util.ctrl.infoMsg("此用户尚未公开其进度日历", title='获取日历失败')
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    cal = icalendar.Calendar()
    cal['prodid'] = 'kyan001.com'
    cal['version'] = '1.1'
    owner = '我' if privatekey else user.nickname
    cal['X-WR-CALNAME'] = '{}的「进度日历」'.format(owner)
    cal['X-WR-TIMEZONE'] = 'Asia/Shanghai'
    cal['X-WR-CALDESC'] = 'http://www.kyan001.com/progress/list'
    for prg in progresses:
        opus = Opus.objects.get(id=prg.opusid)
        create_time = prg.created.strftime('%Y%m%dT%H%M%SZ')
        modify_time = prg.modified.strftime('%Y%m%dT%H%M%SZ')
        url = 'http://www.kyan001.com/progress/detail?id={}'.format(prg.id)
        evnt_create = icalendar.Event()
        evnt_create['uid'] = 'prg:id:{}:create'.format(prg.id)
        evnt_create['description'] = url
        evnt_create['url'] = url
        evnt_create['dtstart'] = create_time
        evnt_create['dtstamp'] = create_time
        evnt_create['summary'] = '开始看《{opus.name}》'.format(opus=opus)
        cal.add_component(evnt_create)
        if prg.status == 'done':
            evnt_done = icalendar.Event()
            evnt_done['uid'] = 'prg:id:{}:done'.format(prg.id)
            evnt_done['description'] = url
            evnt_done['url'] = url
            evnt_done['dtstart'] = modify_time
            evnt_done['dtstamp'] = modify_time
            evnt_done['summary'] = '完成《{opus.name}》'.format(opus=opus)
            cal.add_component(evnt_done)
        elif prg.status == 'giveup':
            evnt_giveup = icalendar.Event()
            evnt_giveup['uid'] = 'prg:id:{}:giveup'.format(prg.id)
            evnt_giveup['description'] = url
            evnt_giveup['url'] = url
            evnt_giveup['dtstart'] = modify_time
            evnt_giveup['dtstamp'] = modify_time
            evnt_giveup['summary'] = '冻结了《{opus.name}》'.format(opus=opus)
            cal.add_component(evnt_giveup)
        elif prg.status == 'inprogress':
            evnt_inprgrss = icalendar.Event()
            evnt_inprgrss['uid'] = 'prg:id:{}:inprogress'.format(prg.id)
            evnt_inprgrss['description'] = url
            evnt_inprgrss['url'] = url
            evnt_inprgrss['dtstart'] = modify_time
            evnt_inprgrss['dtstamp'] = modify_time
            evnt_inprgrss['summary'] = '《{opus.name}》进行至 {prg.current}/{opus.total}'.format(opus=opus, prg=prg)
            cal.add_component(evnt_inprgrss)
        elif prg.status == 'follow':
            evnt_fllw = icalendar.Event()
            evnt_fllw['uid'] = 'prg:id:{}:follow'.format(prg.id)
            evnt_fllw['description'] = url
            evnt_fllw['url'] = url
            evnt_fllw['dtstart'] = modify_time
            evnt_fllw['dtstamp'] = modify_time
            evnt_fllw['summary'] = '《{opus.name}》追剧至 第 {prg.current} 集'.format(opus=opus, prg=prg)
            cal.add_component(evnt_fllw)
    # render
    return HttpResponse(cal.to_ical(), content_type='text/calendar')
