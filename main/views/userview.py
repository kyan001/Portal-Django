from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from main.models import User
from util.ctrl import *

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def getGravatar(email):
    base_src = "https://secure.gravatar.com/avatar/"
    email_md5 = ktk.md5(email) if email else "";
    return base_src + email_md5

def getUserLogin(username, answer):
    if not username:
        raise Exception("username 不能为空")
    if not answer:
        raise Exception("answer 不能为空")
    answer_md5 = ktk.md5(answer)
    user = User.objects.filter(username=username, answer1=answer_md5)
    if len(user) == 0:
        user = User.objects.filter(username=username, answer2=answer_md5)
    if len(user) == 0:
        return None;
    return user

def userAvatar(request, email):
    context = {}
    if email:
        context['headimg'] = getGravatar(email)
    else:
        return infoMsg("请输入email")
    return render_to_response('user/avatar.html', context)

def userUser(request):
    context = {}
    searchable_cols = ('username','id','email');
    try:
        for sc in searchable_cols:
            if sc in request.GET:
                kwargs = {sc : request.GET.get(sc)}
                user = User.objects.get(**kwargs);
                context['headimg'] = getGravatar(user.email);
                context['user'] = user
                return render_to_response('user/index.html', context);
        error_msg = "错误的参数：{0}\n".format(json.dumps(dict(request.GET)))
        error_msg += "请输入 {0} 中的一种".format(', '.join(searchable_cols))
        return infoMsg(error_msg, title='参数错误');
    except User.DoesNotExist:
        return infoMsg("用户 {0} 不存在".format(json.dumps(dict(request.GET))), title='参数错误')

def userSignin(request):
    context = {}
    if 'redirect' in request.GET:
        context['redirect'] = request.GET.get(redirect)
    return render_to_response('user/signin.html', context)

def userGetlogin(request):
    # AJAX
    loginuser = request.session.get('loginuser')
    if loginuser:
        return returnJson(loginuser)
    else:
        return returnJson({'nologinuser':True})


def userCheckLogin(request):
    context = {}
    username = request.POST.get('username')
    answer = request.POST.get('answer')
    if not username:
        return infoMsg("用户名不能为空", title="登陆失败")
    if not answer:
        return infoMsg("答案不能为空", title="登陆失败")
    user = getUserLogin(username, answer)
    if user:
        request.session['loginuser'] = user
    else:
        return infoMsg("等检查用户名与答案组合：username={0},answer={1}".format(username, answer), title="登陆失败")
    if 'redirect' in request.GET:
        return redirect(request.GET.get('redirect'))
    else:
        return redirect('/')
