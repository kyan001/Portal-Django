from functools import partial

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.http import Http404
from django.db.models import Q
from django.core.cache import cache
from django.contrib import messages
from django.utils.translation import gettext as _
from django.template import loader
import icalendar

import util.ctrl
import util.time
import util.user
import util.userexp
from main.models import User, Opus, Progress, Chat
import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


@util.user.login_required
def list(request):
    """进度列表：显示所有进行中、待开始、追剧中的进度"""
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st, stzh in Progress.STATUSES.get('active'):
            prg_list[st] = progresses.filter(status=st)
    else:
        TITLE = _("欢迎使用") + " 「" + _("我的进度") + "」"
        if not user.getChats('received').filter(senderid=Chat.objects.getSyschatUser().id, title=TITLE).exists():
            chat_content = loader.render_to_string("progress/msg-welcome.html", {'title': TITLE})
            Chat.objects.sendBySys(user, title=TITLE, content=chat_content)
    # add exps
    util.userexp.addExp(user, "progress", 1, _("访问「{}」页面").format(_("进度列表")))
    # render
    context = {
        "prglist": prg_list,
    }
    return render(request, "progress/list.html", context)


@util.user.login_required
def archive(request):
    """进度存档：显示所有已完成、已冻结的进度"""
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    prg_list = {}
    if len(progresses):
        for st, stzh in Progress.STATUSES.get('archive'):
            prg_list[st] = progresses.filter(status=st)
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度存档")))
    # render
    context = {
        'prglist': prg_list,
    }
    return render(request, 'progress/archive.html', context)


@util.user.login_required
def search(request):
    """进度搜索：筛选所有进度"""
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('created')
    context['prglist'] = progresses
    # pass searched keyword
    keyword = request.GET.get('kw') or ""
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度搜索")))
    # render
    context = {
        'prglist': progresses,
        'keyword': keyword,
    }
    return render(request, 'progress/search.html', context)


@util.user.login_required
def timeline(request):
    """进度历程：显示所有进度的时间轴"""
    context = {}
    # get user
    user = util.user.getCurrentUser(request)
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    # add timeline info
    now_year = timezone.now().year
    context['prg_timeline_this_year'] = progresses.filter(Q(created__year=now_year) | Q(modified__year=now_year))  # created or modified in this year
    last_year = timezone.now().year - 1
    context['prg_timeline_last_year'] = progresses.filter(Q(created__year=last_year) | Q(modified__year=last_year))  # created or modified in this year
    context['prglist'] = progresses
    # add exps
    util.userexp.addExp(user, 'progress', 1, _("访问「{}」页面").format(_("进度列表")))
    # render
    return render(request, 'progress/timeline.html', context)


@util.user.login_required
def detail(request):
    """进度详情页"""
    errMsg = partial(util.ctrl.infoMsg, title=_('错误'))
    # get inputs
    user = util.user.getCurrentUser(request)
    progressid = request.GET.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # check owner
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("查看")), url='/progress/list')
    # get opus
    opus = Opus.objects.get_or_404(id=progress.opusid)
    # add exp
    util.userexp.addExp(user, "progress", 1, _("查看进度《{}》的详情").format(opus.name))
    # calcs
    aux = {
        "time": {},
        "esti": {},
    }
    aux["time"]["c2n"] = util.time.formatDateToNow(progress.created, "largest")
    aux["time"]["m2n"] = util.time.formatDateToNow(progress.modified, "largest")
    aux["time"]["c2m"] = util.time.formatTimedelta(progress.getTimedelta("c2m"))
    if opus.total and progress.current:  # 非追剧中、非待开始有预计完成时间.
        esti_finish_timedelta = progress.getTimedelta("c2n") / progress.current * (opus.total - progress.current)
        esti_finish_date = progress.modified + esti_finish_timedelta
        aux["esti"]["finish_date"] = esti_finish_date
        aux["esti"]["finish_time"] = util.time.formatDateToNow(esti_finish_date, "largest")
    if progress.current:  # 平均阅读速度.
        speed = progress.getTimedelta("speed")
        if speed:
            aux["time"]["speed"] = util.time.formatTimedelta(speed)
    # render
    context = {}
    context["opus"] = opus
    context["prg"] = progress
    context["aux"] = aux
    return render(request, "progress/detail.html", context)


def imagecolor(request):  # AJAX #PUBLIC
    """异步获取一个url的颜色"""
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


@util.user.login_required
def update(request):
    """detail页面，编辑模式的保存"""
    errMsg = partial(util.ctrl.infoMsg, title=_("更新失败"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"), title=ERROR_TITLE)
    name = request.POST.get('name')
    comment = request.POST.get('comment')
    weblink = request.POST.get('weblink')
    total = request.POST.get('total')
    total = int(total) if total else 0
    current = request.POST.get('current')
    current = int(current)
    if not name:
        return errMsg(_("名称不能为空"))
    if not weblink:
        weblink = ""
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return errMsg(_("初始进度 {c} 不能大于总页数 {t}").format(c=current, t=total))
    # get progress and opus
    progress = Progress.objects.get_or_404(id=progressid)
    opus = progress.opus
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("更新")))
    # add exp
    util.userexp.addExp(user, "progress", 5, _("编辑进度《{}》成功").format(opus.name))
    # save
    progress.current = current
    opus.name = name
    opus.comment = comment
    progress.weblink = weblink
    opus.total = total
    with transaction.atomic():
        opus.save()
        if(progress.setStatusAuto()):
            progress.save()
        else:
            return errMsg(_("储存进度时失败，可能是状态导致的问题"))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(opus.name) + _("已更新"))
    return redirect("/progress/detail?id={}".format(progress.id))


@util.user.login_required
def delete(request):
    """detail 界面点击删除按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("删除失败"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress and opus
    progress = Progress.objects.get_or_404(id=progressid)
    opus = progress.opus
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("删除")))
    # save
    with transaction.atomic():
        progress.delete()
        opus.delete()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("删除进度《{}》").format(opus.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(opus.name) + _("已删除"))
    return redirect("/progress/list")


@util.user.login_required
def deactivate(request):
    """detail 界面点击冻结按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("错误"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress and opus
    progress = Progress.objects.get_or_404(id=progressid)
    opus = progress.opus
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("冻结")))
    # save
    progress.status = 'deactivated'
    progress.save()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("冻结进度《{}》").format(opus.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(opus.name) + _("已冻结"))
    return redirect("/progress/detail?id=" + str(progress.id))


@util.user.login_required
def reactivate(request):
    """detail 界面点击激活进度按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("激活失败"))
    # get inputs
    progressid = request.POST.get('id')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress and opus
    progress = Progress.objects.get_or_404(id=progressid)
    opus = progress.opus
    # check owner
    user = util.user.getCurrentUser(request)
    if progress.userid != user.id:
        return errMsg(_("这个进度不属于您，因此您不能{}该进度").format(_("激活")))
    # save
    progress.resetStatus()
    progress.save()
    # add exp
    util.userexp.addExp(user, "progress", 5, _("恢复已冻结的进度《{}》").format(opus.name))
    # render
    messages.success(request, _("进度") + " 《{}》 ".format(opus.name) + _("已激活"))
    return redirect("/progress/detail?id=" + str(progress.id))


@util.user.login_required
def new(request):
    """list/detail 界面点击新增按钮"""
    # get inputs
    name = request.GET.get("name") or ""
    total = request.GET.get("total") or ""
    weblink = request.GET.get("weblink") or ""
    # add exp
    user = util.user.getCurrentUser(request)
    util.userexp.addExp(user, "progress", 2, _("尝试新增进度"))
    # render
    context = {
        "name": name,
        "total": total,
        "weblink": weblink,
    }
    return render(request, "progress/new.html", context)


@util.user.login_required
def add(request):
    """新增界面点击保存按钮"""
    errMsg = partial(util.ctrl.infoMsg, title=_("新增失败"))
    # get inputs
    name = request.POST.get("name")
    comment = request.POST.get("comment")
    weblink = request.POST.get("weblink")
    if not weblink:
        weblink = ""
    total = request.POST.get("total")
    total = int(total) if total else 0
    current = request.POST.get("current")
    current = int(current)
    if not name:
        return errMsg(_("名称不能为空"))
    # validate
    if current <= 0:
        current = 0
    if total > 0 and current > total:
        return errMsg(_("初始进度 {c} 不能大于总页数 {t}").format(c=current, t=total))
    # add exp
    user = util.user.getCurrentUser(request)
    util.userexp.addExp(user, "progress", 10, _("新增进度《{}》成功").format(name))
    # save
    with transaction.atomic():
        opus = Opus(name=name, comment=comment, total=total)
        opus.save()
        progress = Progress(current=current, opusid=opus.id, userid=user.id, weblink=weblink)
        if(progress.setStatusAuto()):
            progress.save()
        else:
            return errMsg(_("储存进度时失败，可能是状态导致的问题"))
    # render
    return redirect("/progress/detail?id={progress.id}".format(progress=progress))


@util.user.login_required
def setical(request):  # POST
    """用户设置进度日历的界面"""
    use_ical = request.POST.get("useical") or "off"
    icalon = (use_ical == "on")
    user = util.user.getCurrentUser(request)
    user.setUserpermission("progressical", icalon)
    return redirect("/user/setting")


def ical(request):  # GET
    """生成 ical 字符串加入 google calendar"""
    userid = request.GET.get("userid")
    privatekey = request.GET.get("private") or None
    user = User.objects.get_or_404(id=userid)
    if privatekey:  # private mode
        if privatekey != user.privatekey:
            raise Http404(_("获取日历失败") + _("：") + _("用户的私钥不合法"))
    else:  # public mode
        if not user.getUserpermission("progressical"):
            raise Http404(_("获取日历失败") + _("：") + _("此用户尚未公开其进度日历"))
    # get user's progresses
    progresses = Progress.objects.filter(userid=user.id).order_by('-modified')
    cal = icalendar.Calendar()
    cal["prodid"] = "kyan001.com"
    cal["version"] = "1.1"
    cal["X-WR-CALNAME"] = "「" + _("进度日历") + "」" + "@{}".format(user.nickname)
    cal["X-WR-TIMEZONE"] = "Asia/Shanghai"
    cal["X-WR-CALDESC"] = "http://www.kyan001.com/progress/list"
    for prg in progresses:
        create_time = prg.created.strftime('%Y%m%dT%H%M%SZ')
        modify_time = prg.modified.strftime('%Y%m%dT%H%M%SZ')
        url = 'http://www.kyan001.com/progress/detail?id={}'.format(prg.id)
        OPUSNAME = "《{}》".format(prg.opus.name)
        # create event create
        evnt_crt = icalendar.Event()
        evnt_crt['uid'] = 'prg:id:{}:create'.format(prg.id)
        evnt_crt['description'] = url
        evnt_crt['url'] = url
        evnt_crt['dtstart'] = create_time
        evnt_crt['dtstamp'] = create_time
        evnt_crt['summary'] = _("开始看") + " " + OPUSNAME
        cal.add_component(evnt_crt)
        # create event modify
        evnt_mdf = icalendar.Event()
        evnt_mdf['uid'] = 'prg:id:{id}:{st}'.format(id=prg.id, st=prg.status)
        evnt_mdf['description'] = url
        evnt_mdf['url'] = url
        evnt_mdf['dtstart'] = modify_time
        evnt_mdf['dtstamp'] = modify_time
        if prg.status == 'done':
            evnt_mdf['summary'] = _("完成了") + " " + OPUSNAME
        elif prg.status == 'deactivated':
            evnt_mdf['summary'] = _("冻结了") + " " + OPUSNAME
        elif prg.status == 'inprogress':
            evnt_mdf['summary'] = OPUSNAME + " " + _("进行至") + " {c}/{t}".format(c=prg.current, t=prg.opus.total)
        elif prg.status == 'follow':
            evnt_mdf['summary'] = OPUSNAME + " " + _("追剧至") + " " + _("第") + " {} ".format(prg.current) + _("集")
        elif prg.status == 'todo':
            evnt_mdf['summary'] = OPUSNAME + " " + _("加入至") + " " + _("待阅读")
        else:
            evnt_mdf['summary'] = OPUSNAME + " " + _("出错")
        cal.add_component(evnt_mdf)
    # render
    return HttpResponse(cal.to_ical(), content_type='text/calendar')
