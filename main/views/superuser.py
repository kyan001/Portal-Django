from django.shortcuts import render
from main.models import User, UserPermission, Chat, UserPermissionBadge
import util.ctrl
import util.user


def index(request):
    '设置超级管理员'
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get superuser user
    superuser_nickname = '唯笑竹'  # hardcode
    superuser = User.objects.get_or_404(nickname=superuser_nickname)
    # send commands
    title = "《超级管理员操作手册》".format()
    content = '''
        <li class="text-muted">@{user.nickname} 执行了 {category} 的初始化。</li>
        <h5>
            超级管理员操作连接：
        </h5>
        <div class="well">
            <li><a class="" href="/superuser/index">初始化</a></li>
            <li><a class="" href="/superuser/broadcast">广播系统消息</a></li>
            <li><a class="" href="/superuser/updatedb?mode=initbadges">初始化所有徽章</a></li>
            <li><a class="" href='/superuser/updatedb?mode=betauser'>分发 betauser 徽章</a></li>
            <li><a class="" href='/superuser/updatedb?mode=badgedesigner'>分发设计师徽章</a></li>
        </div>
        <li><b>初始化</b>：默认@{superuser.nickname} ，并发送此邮件</li>
        <li><b>广播系统消息</b>：处理、广播系统消息</li>
    '''.format(user=user, superuser=superuser, category='superuser')
    isSuccessed = Chat.objects.sendBySys(superuser, title=title, content=content)
    if not isSuccessed:
        return util.ctrl.infoMsg("发送失败，未知原因，对方用户：@{user.nickname}".format(user=superuser))
    # add superuser permission
    if not superuser.getUserpermission('superuser'):
        superuser.setUserpermission('superuser', True)
        return util.ctrl.infoMsg("@{user.nickname} 已设置为 超级管理员".format(user=superuser))
    return util.ctrl.infoMsg("@{user.nickname} 已是 超级管理员，无需更改".format(user=superuser))


def broadcast(request):
    '''su 发送给所有人的私信'''
    context = {}
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get syschat
    sysuser = User.objects.get_or_404(username='syschat')
    # check superuser
    if not user.getUserpermission('superuser'):
        return util.ctrl.infoMsg("您不具有 超级管理员 权限")
    # get received chats
    chats = Chat.objects.filter(receiverid=sysuser.id).order_by('-created')
    # render
    context['chats'] = chats
    context['sysuser'] = sysuser
    return render(request, 'superuser/broadcast.html', context)


def updatedb(request):
    '''su 更新数据库'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # check superuser
    if not user.getUserpermission('superuser'):
        return util.ctrl.infoMsg("您不具有 {category} 权限".format(category='superuser'))
    # get mode
    mode = request.GET.get('mode')
    if not mode:
        return util.ctrl.infoMsg("需要 Mode 信息")
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
    return util.ctrl.infoMsg("数据库更新完毕，模式 {}".format(mode))


def sendbroadcast(request):
    '''点击 superuser/broadcast 界面中的发送按钮后'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # check superuser
    if not user.getUserpermission('superuser'):
        return util.ctrl.infoMsg("您不具有 {category} 权限".format(category='superuser'))
    # get inputs
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not content:
        return util.ctrl.infoMsg("请填写发送的内容，缺少参数 content")
    # send chat
    receiver_nicknames = []
    receivers = User.objects.exclude(username='syschat')
    for r in receivers:
        isSuccessed = Chat.objects.sendBySys(r, title=title, content=content)
        if not isSuccessed:
            return util.ctrl.infoMsg("发送失败，未知原因，对方用户：@{user.nickname}".format(user=r))
        receiver_nicknames.append(r.nickname)
    # render
    return util.ctrl.infoMsg("发送成功：{}".format(str(receiver_nicknames)), url="/chat/inbox")
