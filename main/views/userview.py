import random
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.cache import cache
from django.contrib import messages
import django.utils.html

from main.models import User, UserExp, Progress, Chat
import util.ctrl
import util.user

import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


def getRandomName():
    '''生成用户昵称'''
    shengmu = ['a', 'i', 'u', 'e', 'o']
    yunmu = ['s', 'k', 'm', 'n', 'r', 'g', 'h', 'p', 'b', 'z', 't', 'd']
    nickname = random.choice(yunmu).upper() + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu)
    users = User.objects.filter(nickname=nickname)
    if len(users) > 0:
        return getRandomName()
    return nickname


def getUserById(user_id):
    '''通过用户名获得用户'''
    if not user_id:
        raise Exception("username 不能为空")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    return user


def getUserInCookie(request):
    '''将 cookie 中存的 user 信息存入 session 并返回'''
    user_id = request.COOKIES.get('user_id')
    user_answer = request.COOKIES.get('user_answer')
    if user_id and user_answer:
        user = getUserById(user_id)
        if user and (user.answer1 == user_answer or user.answer2 == user_answer):
            util.user.rememberLogin(request, user)
            return user
    return False


def checkAnswer(user, answer):
    '''传入用户对象，返回答案对不对'''
    if not user:
        raise Exception("user 不能为空")
    if not answer:
        raise Exception("answer 不能为空")
    answer_md5 = util.ctrl.salty(answer)
    if user.answer1 == answer_md5:
        return True
    if user.answer2 == answer_md5:
        return True
    return False


# -views-----------------------------------------------
def userLogout(request):
    '''用户点击登出'''
    # clean session
    request.session[User.LOGIN_SESSION_KEY] = None
    # create response
    response = redirect('/')
    # clean cookie
    response.delete_cookie('user_id')
    response.delete_cookie('user_answer')
    return response


def userExphistory(request):
    '''用户的所有/某类活跃列表，由 profile 进入'''
    # user check
    user = util.user.getCurrentUser(request)
    if not user:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get inputs
    context = {}
    category = request.GET.get('category')
    view = request.GET.get('view')
    if category:
        userexp = user.getUserExp(category)
        if not userexp:
            return util.ctrl.infoMsg("请求的分类（{category}）不存在".format(category=category), title='访问错误')
        if view == 'full':
            exphistorys = userexp.getExpHistory()
        else:
            exphistorys = userexp.getExpHistory(22)
    else:
        return util.ctrl.infoMsg("请输入请求的分类", title='访问错误')
    # render
    context['userexp'] = userexp
    context['exphistorys'] = exphistorys
    context['view'] = view
    return render(request, 'user/exphistory.html', context)


def userPublic(request):  # public
    '''通过 email/id/nickname 查看用户公开信息'''
    context = {}
    nickname = request.GET.get('nickname')
    if not nickname:
        return util.ctrl.infoMsg("被查看用户的昵称不在参数中", title='参数错误')
    try:
        user = User.objects.get(nickname=nickname)
    except User.DoesNotExist:
        return util.ctrl.infoMsg("用户 @{nickname} 不存在".format(nickname=nickname), title='找不到用户')
    # get user progress counts
    progress_statics = user.getProgressStatics()
    progress_statics_group = []
    for (k, v) in progress_statics.items():
        item = (Progress.objects.getStatusName(k), v['count'])
        progress_statics_group.append(item)
    # add exp to 被查看人
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    _by = request.META.get('REMOTE_HOST') or request.META.get('REMOTE_ADDR')
    userexp.addExp(1, '{} 访问了你的「公开页」'.format(_by))
    # render
    context['user'] = user
    context['prgcounts'] = progress_statics_group
    return render(request, 'user/public.html', context)


def userSetting(request):
    '''修改用户设置'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    icalon = user.getUserpermission('progressical')
    context = {
        'icalon': icalon,
        'privatekey': user.privatekey,
    }
    return render(request, 'user/setting.html', context)


def userProfile(request):
    '''查看当前用户的个人信息，点击右上角昵称进入'''
    context = {}
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get user exps
    exps = []
    lv_notice = []
    userexps = user.getUserExp()
    for ue in userexps:
        explet = (ue, ue.getExpHistory(5))
        exps.append(explet)
        cache_key = 'userexp:{ue.id}:{ue.category}:level'.format(ue=ue)
        cache_timeout = 60 * 60 * 24 * 7 * 2  # 2 weeks
        cached_lv = cache.get(cache_key)
        if cached_lv:  # has cached category:level
            new_lv = ue.level
            if new_lv > cached_lv:
                lv_noticelet = (ue.category_zh(), cached_lv, new_lv)
                lv_notice.append(lv_noticelet)
        cache.set(cache_key, ue.level, cache_timeout)
    # get user progress counts
    progress_statics = user.getProgressStatics()
    done_prg_count = Progress.objects.filter(status='done').count()
    if done_prg_count >= 25:
        user.setUserpermission('wellread', True)
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '查看用户个人信息')
    # render
    context['prgstatics'] = progress_statics.values()
    context['exps'] = exps
    context['lvnotice'] = lv_notice
    return render(request, 'user/profile.html', context)


# -Signup-----------------------------------------------
def userSignup(request):  # PUBLIC
    '''点击注册按钮后页面'''
    context = {}
    if 'redirect' in request.GET:
        context['redirect'] = request.GET.get('redirect')
    elif 'HTTP_REFERER' in request.META:
        context['redirect'] = request.META.get('HTTP_REFERER')
    return render(request, 'user/signup.html', context)


def userNewUser(request):  # POST
    '''新用户点击提交注册按钮后'''
    username = request.POST.get('username')
    question = request.POST.get('question')
    answer1 = request.POST.get('answer1')
    answer2 = request.POST.get('answer2')
    tip = request.POST.get('tip')
    nickname = request.POST.get('nickname')
    email = request.POST.get('email')
    # check musts
    if not username:
        return util.ctrl.infoMsg("“用户名” 不能为空", title="注册失败")
    if not question:
        return util.ctrl.infoMsg("“问题” 不能为空", title="注册失败")
    if not answer1:
        return util.ctrl.infoMsg("“答案” 不能为空", title="注册失败")
    if not email:
        return util.ctrl.infoMsg("“邮箱” 不能为空", title="注册失败")
    # auto fills
    if not nickname:
        nickname = getRandomName()
    answer1 = util.ctrl.salty(answer1)
    answer2 = util.ctrl.salty(answer2) if answer2 else None
    if not tip:
        tip = None
    # check conflicts
    if len(User.objects.filter(username=username)) != 0:
        return util.ctrl.infoMsg("用户名 '{username}' 已存在！".format(username=username), title="注册失败")
    if len(User.objects.filter(nickname=nickname)) != 0:
        return util.ctrl.infoMsg("昵称 '{nickname}' 已存在！".format(nickname=nickname), title="注册失败")
    if len(User.objects.filter(email=email)) != 0:
        return util.ctrl.infoMsg("邮箱 '{email}' 已存在！".format(email=email), title="注册失败")
    # check literally
    if " " in username:
        return util.ctrl.infoMsg("用户名 '{username}' 只应包含数字、字母、和英文句号！".format(username=username), title="注册失败")
    if " " in nickname:
        return util.ctrl.infoMsg("昵称 '{nickname}' 只应包含字母和汉字！".format(nickname=nickname), title="注册失败")
    # create into db
    user = User(username=username, question=question, answer1=answer1, answer2=answer2, tip=tip, nickname=nickname, email=email)
    user.save()
    # add betauser badge
    user.setUserpermission('betauser', True)
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '注册成功')
    # render
    return util.ctrl.infoMsg(" {user.username} 注册成功！\n您是网站第 {user.id} 位用户。\n请登入以便我们记住您！".format(user=user), url='/user/signin', title="欢迎加入")


def userHeadimgUpdate(request):
    '''点击修改头像后处理更换头像'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.artist.loginToContinue(request)
    headimg = request.FILES.get('headimg')
    user.headimg = headimg
    user.save()
    messages.success(request, '修改头像成功')
    return redirect('/user/profile')


# -Signin-----------------------------------------------
def userSignin(request):
    '''点击登入后的页面，供输入用户名/密码'''
    # check if already logged in
    from_ = request.GET.get("from") or ""
    current_user = util.user.getCurrentUser(request)
    if current_user:
        return util.ctrl.infoMsg("您已经以 {username} 的身份登入了，请勿重复登入".format(username=current_user.username), title="登入失败", url="/")
    # render
    context = {
        'request': request,
        'from': from_,
    }
    if 'HTTP_REFERER' in request.META:
        context['redirect'] = request.META.get('HTTP_REFERER')
    return render(request, 'user/signin.html', context)


def userForgetanswer(request):
    '登入页面点击忘记回答'
    context = {}
    # TODO: Not worked on Server
    # content = '''
    #     <li>您在 <a href='http://superfarmer.net' target='_blank'>superfarmer.net</a> 申请了“忘记答案/密码”</li>
    #     <li>请点击下面的连接重置答案/密码</li>
    #     <li>下面的连接有效期只有 60 分钟。</li>
    #     <li>如果连接无法打开，请在复制后在浏览器中打开：</li>
    #     <a href='http://www.superfarmer.net/user/resetanswer/'>http://www.superfarmer.net/user/resetanswer/</a>
    # '''
    # result = sendEmail(content, 'kai@superfarmer.net', subject='忘记密码找回注册')
    # if not result:
    #     return util.ctrl.infoMsg("发送邮件失败："+ json.dumps(result), title="发送失败")
    return render(request, 'user/forgetanswer.html', context)


def userForgetusername(request):
    email = request.POST.get('email')
    if not email:
        return render(request, 'user/forgetusername.html')
    target_user = User.objects.filter(email=email)
    if len(target_user) == 0:
        return util.ctrl.infoMsg("此邮箱（{}）尚未被注册".format(email), title="找回用户名")
    else:
        user = target_user.get()
        username = user.username
        step = random.randint(2, 3)  # a*c*e*g or a**d**g
        username_part = ((step - 1) * '*').join(username[::step])  # show username partial
        username_part += '*' * (len(username) - len(username_part))  # make it full length
        username_part = username_part[:-1] + username[-1]  # last letter is shown
        # send chat
        chat_content = '''
            有人正在通过邮件的方式找回您的用户名。
            <hr/>
            他输入的邮件是：<pre>{eml}</pre>
            他得到的用户名是：<pre>{un} </pre>
            <hr/>
            若此操作不是您所为，请联系管理员 @系统消息
        '''.format(eml=email, un=username_part)
        msg = Chat.objects.sendBySys(user, title="有人正在通过邮件的方式找回您的用户名", content=chat_content)
        msg.save()
        infomsg = """
            出于安全考虑，您的用户名未全部显示，每个 <code>*</code> 代表一个字符。
            <hr/>
            你的用户名是：<pre>{}</pre>
            <hr/>
            一封包含此次操作信息的站内信已经发送给您。
        """.format(username_part)
        return util.ctrl.infoMsg(infomsg, title='找回用户名')


def userCheckLogin(request):  # POST
    '''用户点击登入后：判断用户是否可以登入'''
    # get posts
    username = request.POST.get('username')
    answer = request.POST.get('answer')
    rememberme = request.POST.get('rememberme') or 'off'
    from_ = request.POST.get('from') or ''
    _failto = request.META.get('HTTP_REFERER', "/user/signin")
    if not username:
        messages.error(request, "登入失败：用户名不能为空")
        return redirect(_failto)
    if not answer:
        messages.error(request, "登入失败：答案不能为空")
        return redirect(_failto)
    # check username vs. answer
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "登入失败：找不到用户名为 {} 的用户".format(username))
        return redirect(_failto)
    if user.getUserpermission('signin') is False:  # None is OK, True is OK, False is not OK
        messages.error(request, '登入失败：您已被禁止登入，请联系管理员')
        return redirect(_failto)
    if checkAnswer(user, answer):
        util.user.rememberLogin(request, user)
    else:
        messages.error(request, "登入失败：用户名与答案不匹配")
        return redirect(_failto)
    # redirections
    to_ = from_ or '/'
    response = redirect(to_)
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '登入成功')
    # remove old msgs
    msg_title = 'Hi, @{user.nickname}'.format(user=user)
    sysuser = Chat.objects.getSyschatUser()
    old_msg = user.getChats('received').filter(senderid=sysuser.id, title=msg_title)
    has_old_msg = old_msg.exists()
    old_msg.delete()
    # send chat
    chat_content = '''
        欢迎您归来，开始您的网站之旅吧！<br/>
        <li>访问 <a href="/progress/list">我的进度</a> 查看进度列表</li>
        <li>访问 <a href="/user/profile">我的账号信息</a> 查看您的活跃度、进度统计</li>
        <li>访问 <a href="/chat/conversation?mode=quicknote">临时笔记</a> 随手记录您的想法</li>
        <li>遇到问题或想 #提建议 ，请发消息给 @系统消息 ！</li>
    '''
    new_msg = Chat.objects.sendBySys(user, title=msg_title, content=chat_content)
    if has_old_msg:
        new_msg.isread = True
        new_msg.save()
    # set cookie
    if rememberme == 'on':
        oneweek = 60 * 60 * 24 * 7
        response.set_cookie('user_id', user.id, max_age=oneweek)
        response.set_cookie('user_answer', user.answer1, max_age=oneweek)
    return response


def userGetQuestionAndTip(request):  # AJAX
    '''登入时：通过用户名得到用户问题'''
    username = request.GET.get('username')
    if not username:
        return util.ctrl.returnJsonError('用户名不能为空')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return util.ctrl.returnJsonError("登入失败：找不到用户名为 {} 的用户".format(username))
    if user:
        question = user.question
        tip = user.tip
        return util.ctrl.returnJson({
            'question': question,
            'tip': tip,
        })
    else:
        return util.ctrl.returnJsonError('用户未找到：{username}'.format(username=username))


def userGetUnreadCount(request):  # AJAX
    '''顶部用户栏：更新当前用户的未读消息数目'''
    # from session
    user = util.user.getCurrentUser(request)
    result = {}
    # from cookies
    if not user:
        user = getUserInCookie(request)
    # get user's gravatar
    if user:
        unread_count = user.getChats('unread').count()
        result['unreadcount'] = unread_count
        result['msgs'] = []
        if unread_count:
            unread_chats = user.getChats('unread')
            for uc in unread_chats:
                sender = User.objects.get(id=uc.senderid)
                words = uc.title or uc.content
                words = django.utils.html.strip_tags(words)
                if len(words) > 12:
                    words = words[0:12] + '...'
                result['msgs'].append({
                    'sender': sender.nickname,
                    'words': words,
                })
        return util.ctrl.returnJson(result)
    else:
        return util.ctrl.returnJsonResult('nologinuser')


# -Validations------------------------------------------
def userValidateUsername(request):  # AJAX
    '''注册/登入时：用户名是否可用'''
    username = request.GET.get('username')
    result = {}
    if not username:
        return util.ctrl.returnJsonError('用户名不能为空')
    users = User.objects.filter(username=username)
    if len(users) == 1:
        result['exist'] = True
        potential_users = User.objects.filter(username__startswith=username)
        if len(potential_users) == 1:
            result['unique'] = True
        else:
            result['unique'] = False
    else:
        result['exist'] = False
    return util.ctrl.returnJson(result)


def userValidateNickname(request):  # AJAX
    '''注册时：昵称是否可用'''
    nickname = request.GET.get('nickname')
    result = {}
    if not nickname:
        return util.ctrl.returnJsonError('昵称不能为空')
    users = User.objects.filter(nickname=nickname)
    if len(users) != 0:
        result['exist'] = True
    else:
        result['exist'] = False
    return util.ctrl.returnJson(result)


def userValidateEmail(request):  # AJAX
    '''注册时：邮箱是否可用'''
    email = request.GET.get('email')
    result = {}
    if not email:
        return util.ctrl.returnJsonError('邮箱不能为空')
    users = User.objects.filter(email=email)
    if len(users) != 0:
        result['exist'] = True
    else:
        result['exist'] = False
    return util.ctrl.returnJson(result)
