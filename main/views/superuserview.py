from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import *
from main.models import *
from django.views.decorators.csrf import csrf_exempt
import util.ctrl
def superuserIndex(request):
    '设置超级管理员'
    context = {'request': request}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 id：{id} 并不存在".format(id=str(loginuser['id'])));
    # get superuser user
    superuser_nickname='唯笑竹'
    try:
        superuser = User.objects.get(nickname=superuser_nickname)
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 @{nickname} 并不存在".format(nickname=superuser_nickname));
    # send commands
    title = "你好，{category_name}".format(category_name=UserPermission.objects.getCategoryName('superuser'))
    content = '''
        <li class="text-muted">@{user.nickname} 执行了 {category_name} 的初始化。</li>
        超级管理员操作连接：
        <li><a href="/superuser/index">初始化</a>：默认@{superuser.nickname} ，并发送此邮件</li>
        <li><a href="/superuser/broadcast">广播系统消息</a>：处理、广播系统消息</li>
    '''.format(user=user, superuser=superuser, category_name=UserPermission.objects.getCategoryName('superuser'));
    isSuccessed = Chat.objects.sendBySys(superuser, title=title, content=content)
    if not isSuccessed:
        return util.ctrl.infoMsg("发送失败，未知原因，对方用户：@{user.nickname}".format(user=superuser));
    # add superuser permission
    if not superuser.getUserpermission('superuser'):
        superuser.setUserpermission('superuser', True)
        return util.ctrl.infoMsg("@{user.nickname} 已设置为 {category_name}".format(user=superuser, category_name=UserPermission.objects.getCategoryName('superuser')));
    return util.ctrl.infoMsg("@{user.nickname} 已是 {category_name}，无需更改".format(user=superuser, category_name=UserPermission.objects.getCategoryName('superuser')));

def superuserBroadcast(request):
    '''su 发送给所有人的私信'''
    context = {'request': request}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 id：{id} 并不存在".format(id=str(loginuser['id'])));
    # get syschat
    try:
        sysuser = User.objects.get(username='syschat')
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 username：'syschat' 并不存在");
    # check superuser
    if not user.getUserpermission('superuser'):
        return util.ctrl.infoMsg("您不具有 {category_name} 权限".format(category_name=UserPermission.objects.getCategoryName('superuser')));
    # get received chats
    chats = Chat.objects.filter(receiverid=sysuser.id).order_by('-created')
    # render
    context['chats'] = chats
    context['user'] = sysuser
    return render_to_response('superuser/broadcast.html', context);

@csrf_exempt
def superuserSendbroadcast(request):
    '''点击 superuser/broadcast 界面中的发送按钮后'''
    context = {'request': request}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 id：{id} 并不存在".format(id=str(loginuser['id'])));
    # check superuser
    if not user.getUserpermission('superuser'):
        return util.ctrl.infoMsg("您不具有 {category_name} 权限".format(category_name=UserPermission.objects.getCategoryName('superuser')));
    # get inputs
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not content:
        return util.ctrl.infoMsg("请填写发送的内容，缺少参数 content");
    # send chat
    receiver_nicknames = []
    receivers = User.objects.exclude(username='syschat')
    for r in receivers:
        isSuccessed = Chat.objects.sendBySys(r, title=title, content=content)
        if not isSuccessed:
            return util.ctrl.infoMsg("发送失败，未知原因，对方用户：@{user.nickname}".format(user=r));
        receiver_nicknames.append(r.nickname)
    # render
    return util.ctrl.infoMsg("发送成功：{}".format(str(receiver_nicknames)))
