import random
from django.contrib import messages
from django.shortcuts import redirect
from main.models import User
import util.ctrl


def getCurrentUser(request):
    """Get logged user from session"""
    userid = request.session.get(User.LOGIN_SESSION_KEY)
    if not userid:
        return None
    user = User.objects.get_or_none(id=userid)
    return user or False


def checkAnswer(user, answer_raw):
    '''传入用户对象，返回答案对不对'''
    if not user:
        raise Exception("user 不能为空")
    if not answer_raw:
        raise Exception("answer 不能为空")
    answer_md5 = util.ctrl.salty(answer_raw)
    return (user.answer1 == answer_md5) or (user.answer2 == answer_md5)


def rememberLogin(request, user):
    """Remember logged user"""
    if not user:
        return False
    request.session[User.LOGIN_SESSION_KEY] = user.id  # remember login
    return True


def cookieLogout(response):
    """delete login info from cookie"""
    response.delete_cookie('user_id')
    response.delete_cookie('user_answer')
    return response


def addCookieLogin(response, user, answer_raw):
    """add login info into cookie"""
    oneweek = 60 * 60 * 24 * 7
    response.set_cookie('user_id', user.id, max_age=oneweek)
    response.set_cookie('user_answer', answer_raw, max_age=oneweek)
    return response


def getCookieLogin(request):
    '''将 cookie 中存的 user 信息存入 session 并返回'''
    user_id = request.COOKIES.get('user_id')
    user_answer = request.COOKIES.get('user_answer')
    if not user_id or not user_answer:
        return None
    user = User.objects.get_or_none(id=user_id)
    if user and checkAnswer(user, user_answer):
        rememberLogin(request, user)
        return user
    return None


def getRandomName():
    '''生成用户昵称'''
    shengmu = ['a', 'i', 'u', 'e', 'o']
    yunmu = ['s', 'k', 'm', 'n', 'r', 'g', 'h', 'p', 'b', 'z', 't', 'd']
    nickname = random.choice(yunmu).upper() + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu)
    users = User.objects.filter(nickname=nickname)
    if len(users) > 0:
        return getRandomName()
    return nickname


def loginToContinue(request):
    """Show a message, goto login page, and then go back to current page"""
    messages.error(request, '此页面需要用户信息，\n请登入/注册后再访问。')
    _from = request.get_full_path()
    return redirect('/user/signin?from={}'.format(_from))
