from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import User, UserExp, Progress
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def getGravatarUrl(email):
    '''获取用户gravatar地址'''
    base_src = "https://secure.gravatar.com/avatar/"
    email_md5 = ktk.md5(email) if email else "";
    return base_src + email_md5

def getRandomName():
    '''生成用户昵称'''
    shengmu = ['a','i','u','e','o']
    yunmu = ['s','k','m','n','r','g','h','p','b','z','t','d']
    nickname = random.choice(yunmu).upper() + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu)
    users = User.objects.filter(nickname=nickname)
    if len(users) > 0:
        return getRandomName()
    return nickname;

def getUser(username):
    '''通过用户名获得用户'''
    if not username:
        raise Exception("username 不能为空")
    try:
        user = User.objects.get(username=username);
    except User.DoesNotExist:
        return None;
    return user;

def getUserById(user_id):
    '''通过用户名获得用户'''
    if not user_id:
        raise Exception("username 不能为空")
    try:
        user = User.objects.get(id=user_id);
    except User.DoesNotExist:
        return None;
    return user;

def checkAnswer(user, answer):
    '''传入用户对象，返回答案对不对'''
    if not user:
        raise Exception("user 不能为空")
    if not answer:
        raise Exception("answer 不能为空")
    answer_md5 = salty(answer)
    if user.answer1 == answer_md5:
        return True;
    if user.answer2 == answer_md5:
        return True;
    return False;

#--views-----------------------------------------------

def userLogout(request):
    '''用户点击登出'''
    # clean session
    request.session['loginuser'] = None;
    # create response
    if 'HTTP_REFERER' in request.META:
        response = redirect(request.META.get('HTTP_REFERER'))
    else:
        response = redirect('/')
    # clean cookie
    response.delete_cookie('user_id')
    response.delete_cookie('user_answer')
    return response;

def userAvatar(request, email): # public
    '''通过 email 取回 gravatar'''
    context = {}
    if email:
        context['headimg'] = getGravatarUrl(email)
    else:
        return infoMsg("请输入email")
    return render_to_response('user/avatar.html', context)

def userExphistory(request):
    '''用户的所有/某类活跃列表，由 profile 进入'''
    # user check
    user = request.session.get('loginuser')
    if not user:
        return infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    user = User.objects.get(id=user['id'])
    # get inputs
    context = {}
    category = request.GET.get('category')
    if category:
        if category not in UserExp.category_pool.get('all'):
            return infoMsg("请求的分类（{0}）不存在".format(category), title='访问错误')
        userexp = user.getUserExp(category)
        exphistorys = userexp.getExpHistory()
    # render
    context['user'] = user
    context['userexp'] = userexp
    context['exphistorys'] = exphistorys
    return render_to_response('user/exphistory.html', context)

def userUser(request): # public
    '''通过 email/id/nickname 查看用户公开信息'''
    context = {}
    searchable_cols = ('nickname','id','email');
    try:
        for sc in searchable_cols:
            if sc in request.GET:
                kwargs = {sc : request.GET.get(sc)}
                user = User.objects.get(**kwargs);
                context['headimg'] = getGravatarUrl(user.email);
                context['user'] = user
                return render_to_response('user/user.html', context);
        error_msg = "错误的参数：{0}\n".format(json.dumps(dict(request.GET)))
        error_msg += "请输入 {0} 中的一种".format(', '.join(searchable_cols))
        return infoMsg(error_msg, title='参数错误');
    except User.DoesNotExist:
        return infoMsg("用户 {0} 不存在".format(json.dumps(dict(request.GET))), title='参数错误')

def userProfile(request):
    '''查看当前用户的个人信息，点击右上角昵称进入'''
    context = {}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return infoMsg("您查找的用户id {} 并不存在".format(str(loginuser['id'])));
    # get user exps
    userexps = user.getUserExp()
    exps = []
    for ue in userexps:
        explet = (ue, ue.getExpHistory(5))
        exps.append(explet)
    # get user progress counts
    progress_counts = user.getProgressCounts();
    progress_counts_group = []
    print(progress_counts)
    for (k, v) in progress_counts.items():
        item = (Progress.objects.getStatusName(k), v)
        progress_counts_group.append(item)
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '查看用户私人信息')
    # render
    context['user'] = user
    context['headimg'] = getGravatarUrl(user.email);
    context['prgcounts'] = progress_counts_group
    context['exps'] = exps
    return render_to_response('user/profile.html', context)

#-Signup-----------------------------------------------
def userSignup(request):
    '''点击注册按钮后页面'''
    context = {}
    if 'redirect' in request.GET:
        context['redirect'] = request.GET.get('redirect')
    elif 'HTTP_REFERER' in request.META:
        context['redirect'] = request.META.get('HTTP_REFERER')
    return render_to_response('user/signup.html', context)

@csrf_exempt
def userNewUser(request):
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
        return infoMsg("“用户名” 不能为空", title="注册失败")
    if not question:
        return infoMsg("“问题” 不能为空", title="注册失败")
    if not answer1:
        return infoMsg("“答案” 不能为空", title="注册失败")
    if not email:
        return infoMsg("“邮箱” 不能为空", title="注册失败")

    # auto fills
    if not nickname:
        nickname = getRandomName();
    answer1 = salty(answer1)
    answer2 = salty(answer2) if answer2 else None;
    if not tip:
        tip = None;

    # check conflicts
    if len(User.objects.filter(username=username)) != 0:
        return infoMsg("用户名 '{0}' 已存在！".format(username), title="注册失败")
    if len(User.objects.filter(nickname=nickname)) != 0:
        return infoMsg("昵称 '{0}' 已存在！".format(nickname), title="注册失败")
    if len(User.objects.filter(email=email)) != 0:
        return infoMsg("邮箱 '{0}' 已存在！".format(email), title="注册失败")

    # check literally
    if " " in username:
        return infoMsg("用户名 '{0}' 只应包含数字、字母、和英文句号！".format(username), title="注册失败")
    if " " in nickname:
        return infoMsg("昵称 '{0}' 只应包含字母和汉字！".format(nickname), title="注册失败")

    # create into db
    user = User(username=username, question=question, answer1=answer1, answer2=answer2, tip=tip, nickname=nickname, email=email)
    user.setCreated();
    user.save();

    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '注册成功')

    # render
    return infoMsg(" {0} 注册成功！\n您是网站第 {1} 位用户。\n请登入以便我们记住您！".format(username, str(user.id)), url='/user/signin', title="欢迎加入")

#-Signin-----------------------------------------------
def userSignin(request):
    '''点击登入后的页面，供输入用户名/密码'''
    # check if already logged in
    current_user = request.session.get('loginuser');
    if current_user:
        return infoMsg("您已经以 {0} 的身份登入了，请勿重复登入".format(current_user['username']), title="登入失败", url="/")
    # render
    context = {}
    if 'HTTP_REFERER' in request.META:
        context['redirect'] = request.META.get('HTTP_REFERER')
    return render_to_response('user/signin.html', context)

def userForgetanswer(request):
    '登入页面点击忘记回答'
    context = {}
    content = '''
        <li>您在 <a href='http://superfarmer.net' target='_blank'>superfarmer.net</a> 申请了“忘记答案/密码”</li>
        <li>请点击下面的连接重置答案/密码</li>
        <li>下面的连接有效期只有 60 分钟。</li>
        <li>如果连接无法打开，请在复制后在浏览器中打开：</li>
        <a href='http://portal.superfarmer.net/user/resetanswer/'>http://portal.superfarmer.net/user/resetanswer/</a>
    '''
    # TODO: Not worked on Server
    # result = sendEmail(content, 'kai@superfarmer.net', subject='忘记密码找回注册')
    # if not result:
    #     return infoMsg("发送邮件失败："+ json.dumps(result), title="发送失败")
    return render_to_response('user/forgetanswer.html', context)


@csrf_exempt
def userCheckLogin(request):
    '''用户点击登入后：判断用户是否可以登入'''
    # get posts
    context = {}
    username = request.POST.get('username')
    answer = request.POST.get('answer')
    rememberme = request.POST.get('rememberme')
    if not username:
        return infoMsg("用户名不能为空", title="登入失败")
    if not answer:
        return infoMsg("答案不能为空", title="登入失败")
    # check username vs. answer
    user = getUser(username)
    if checkAnswer(user, answer):
        request.session['loginuser'] = user.toArray()
    else:
        return infoMsg("用户名/答案不对：\n用户名：{0}\n输入的答案/密码：{1}".format(username, answer), title="登入失败")
    # redirections
    redirect_url = request.POST.get('redirect')
    redirect_to_home = (
        '/user/newuser',
        '/user/newuser/',
        '/user/signin',
        '/user/signin/',
        '/user/signup',
        '/user/signup/'
        )
    if redirect_url:
        response = redirect(redirect_url)
    else:
        response = redirect('/')
    for urllet in redirect_to_home:
        if urllet in redirect_url:
            response = redirect('/')
    # add exp
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='user')
    userexp.addExp(1, '登陆成功')
    # set cookie
    if rememberme == 'yes':
        oneweek = 60*60*24*7
        response.set_cookie('user_id', user.id, max_age=oneweek)
        response.set_cookie('user_answer', user.answer1, max_age=oneweek)
    return response

def userGetQuestionAndTip(request): #AJAX
    '''登入时：通过用户名得到用户问题'''
    username = request.GET.get('username')
    if not username:
        return returnJsonError('用户名不能为空')
    user = getUser(username)
    if user:
        question = user.question
        tip = user.tip
        return returnJson({
            'question' : question,
            'tip' : tip,
        });
    else:
        return returnJsonError('用户未找到：{0}'.format(username))

def userGetloginerInfo(request): # AJAX
    '''顶部用户栏：获取当前登入用户的信息'''
    # from session
    loginuser = request.session.get('loginuser')
    # from cookies
    if not loginuser:
        user_id = request.COOKIES.get('user_id')
        user_answer = request.COOKIES.get('user_answer')
        if user_id and user_answer:
            user = getUserById(user_id)
            if user.answer1 == user_answer or user.answer2 == user_answer:
                request.session['loginuser'] = user.toArray()
                loginuser = user.toArray();
    # get user's gravatar
    if loginuser:
        loginuser['avatar'] = getGravatarUrl(loginuser['email'])
        return returnJson(loginuser)
    else:
        return returnJsonResult('nologinuser')

#-Validations------------------------------------------
def userValidateUsername(request): #AJAX
    '''注册/登入时：用户名是否可用'''
    username = request.GET.get('username');
    result = {}
    if not username:
        return returnJsonError('用户名不能为空')
    users = User.objects.filter(username=username);
    if len(users) == 1:
        result['exist'] = True
        potential_users = User.objects.filter(username__startswith=username)
        if len(potential_users) == 1:
            result['unique'] = True
        else:
            result['unique'] = False
    else:
        result['exist'] = False
    return returnJson(result)

def userValidateNickname(request): #AJAX
    '''注册时：昵称是否可用'''
    nickname = request.GET.get('nickname');
    result = {}
    if not nickname:
        return returnJsonError('昵称不能为空')
    users = User.objects.filter(nickname=nickname);
    if len(users) != 0:
        result['exist'] = True
    else:
        result['exist'] = False
    return returnJson(result)

def userValidateEmail(request): #AJAX
    '''注册时：邮箱是否可用'''
    email = request.GET.get('email');
    result = {}
    if not email:
        return returnJsonError('邮箱不能为空')
    users = User.objects.filter(email=email)
    if len(users) != 0:
        result['exist'] = True
    else:
        result['exist'] = False
    return returnJson(result)
