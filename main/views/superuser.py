from django.shortcuts import render
from django.utils.translation import gettext as _

from main.models import User, UserPermission, Chat, UserPermissionBadge
import util.ctrl
import util.user


@util.user.login_required
def index(request):
    """设置超级管理员"""
    user = util.user.getCurrentUser(request)
    # get superuser user
    superuser_nickname = '唯笑竹'  # hardcode
    superuser = User.objects.get_or_404(nickname=superuser_nickname)
    # send commands
    title = _("《{}操作手册》").format(_("超级管理员"))
    operations = [
        {
            "name": _("初始化"),
            "href": "/superuser/index",
            "desc": _("默认设置 @{} 为超级管理员，并向其发送此邮件").format(superuser.nickname),
        },
        {
            "name": _("广播系统消息"),
            "href": "/superuser/broadcast",
            "desc": _("查看发给系统的消息，广播消息"),
        },
        {
            "name": _("初始化所有徽章"),
            "href": "/superuser/updatedb?mode=initbadges",
            "desc": _("刷新数据库中徽章的信息"),
        },
        {
            "name": _("分发 Betauser 徽章"),
            "href": "/superuser/updatedb?mode=betauser",
            "desc": _("对网站前 100 名用户添加 Betauser 徽章"),
        },
        {
            "name": _("分发设计师徽章"),
            "href": "/superuser/updatedb?mode=badgedesigner",
            "desc": _("对所有徽章的设计师添加 Designer 徽章"),
        },
    ]
    # generate html
    content_links = "".join(["<li><a href='{h}'>{n}</a></li> <ul><li>{d}</li></ul>".format(h=o.get("href"), n=o.get("name"), d=o.get("desc")) for o in operations])
    content = "".join([
        "<li class='text-muted'>@{u} {d}</li>".format(u=user.nickname, d=_("执行了超级管理员的初始化。")),
        "<h5>{}</h5>".format(_("超级管理员操作连接：")),
        "<div class='well'>{}</div>".format(content_links),
    ])
    # send message to suepruser
    isSuccessed = Chat.objects.sendBySys(superuser, title=title, content=content)
    if not isSuccessed:
        return util.ctrl.infoMsg(_("发送失败，未知原因。用户：@{}").format(superuser.nickname))
    # add superuser permission
    if not superuser.getUserpermission('superuser'):
        superuser.setUserpermission('superuser', True)
        return util.ctrl.infoMsg(_("@{} 已设置为超级管理员").format(superuser.nickname))
    return util.ctrl.infoMsg(_("@{} 已是超级管理员，无需更改").format(superuser.nickname))


@util.user.login_required
@util.user.superuser_required
def broadcast(request):
    '''su 发送给所有人的私信'''
    context = {}
    user = util.user.getCurrentUser(request)
    # get syschat
    sysuser = User.objects.get_or_404(username='syschat')
    # get received chats
    chats = Chat.objects.filter(receiverid=sysuser.id).order_by('-created')
    # render
    context['chats'] = chats
    context['sysuser'] = sysuser
    return render(request, 'superuser/broadcast.html', context)


@util.user.login_required
@util.user.superuser_required
def updatedb(request):
    '''su 更新数据库'''
    # get mode
    mode = request.GET.get('mode')
    if not mode:
        return util.ctrl.infoMsg(_("{} 参数不能为空").format("Mode"), title=_('错误'))
    # main codes
    if 'initbadges' == mode:
        # update userPermissionBadge
        badge_list = [
            {
                'category': 'superuser',
                'isallowed': True,
                'image': '/static/img/badges/superuser.png',
                'description': 'For who owns the site',
                'requirement': '在你成为网站超级管理员的瞬间，这枚徽章将会自动出现。',
                'designernname': '唯笑竹',
            },
            {
                'category': 'signin',
                'isallowed': False,
                'image': '/static/img/badges/signin-no.png',
                'description': '此用户被禁止登入',
                'requirement': '当你做了什么事被关入小黑屋的时候，这枚徽章将会自动出现。\n（然而现在并没有什么小黑屋）\n一些不准许登入的系统用户也会拥有此徽章）',
                'designernname': '唯笑竹',
            },
            {
                'category': 'betauser',
                'isallowed': True,
                'image': '/static/img/badges/betauser.png',
                'description': '网站的前 100 名用户',
                'requirement': '这是对你曾经注册支持过一个不太成熟的网站的证明。',
                'designernname': '唯笑竹',
            },
            {
                'category': 'wellread',
                'isallowed': True,
                'image': '/static/img/badges/wellread.png',
                'description': '饱读诗书',
                'requirement': '这是完成了超过 25 个进度的证明，说你饱读诗书也不为过。',
                'designernname': 'Winnie',
            },
            {
                'category': 'badgedesigner',
                'isallowed': True,
                'image': '/static/img/badges/badgedesigner.png',
                'description': '徽章设计师',
                'requirement': '你将会获得这枚徽章，以感谢对徽章设计的贡献。',
                'designernname': 'Winnie',
            },
            {
                'category': 'progressical',
                'isallowed': True,
                'image': '/static/img/badges/ical.png',
                'description': '与民同乐',
                'requirement': '这枚徽章仅授予愿意将「进程日历」分享给他人的用户',
                'designernname': '唯笑竹',
            },
        ]
        for badge in badge_list:
            upb, iscreated = UserPermissionBadge.objects.update_or_create(category=badge['category'], isallowed=badge['isallowed'], defaults=badge)
    if 'badgedesigner' == mode:
        # update badgedesigner badge
        badges = UserPermissionBadge.objects.all()
        for b in badges:
            designer = b.designer
            if designer:
                designer.setUserpermission('badgedesigner', True)
    if 'betauser' == mode:
        top100users = User.objects.all()[0:100]
        for u in top100users:
            u.setUserpermission('betauser', True)
    # render
    return util.ctrl.infoMsg(_("数据库更新完毕，模式 {}").format(mode))


@util.user.login_required
@util.user.superuser_required
def sendbroadcast(request):
    '''点击 superuser/broadcast 界面中的发送按钮后'''
    user = util.user.getCurrentUser(request)
    # get inputs
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not content:
        return util.ctrl.infoMsg(_("{} 参数不能为空").format("Content"), title=_('错误'))
    # send chat
    receiver_nicknames = []
    receivers = User.objects.exclude(username='syschat')
    for r in receivers:
        isSuccessed = Chat.objects.sendBySys(r, title=title, content=content)
        if not isSuccessed:
            return util.ctrl.infoMsg(_("发送失败，未知原因。用户：@{}").format(r.nickname))
        receiver_nicknames.append(r.nickname)
    # render
    return util.ctrl.infoMsg(_("发送成功") + _("：") + str(receiver_nicknames), url="/chat/inbox")
