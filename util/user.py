import random
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _

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
    """传入用户对象，返回答案对不对"""
    if not user:
        raise Exception(_("{} 参数不能为空").format('User'))
    if not answer_raw:
        raise Exception(_("{} 参数不能为空").format('Answer'))
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
    response.delete_cookie('user_token')
    return response


def generateUserToken(user):
    """generate user login token, saved in cookie"""
    return util.ctrl.salty(str(user.id) + user.answer1)


def checkUserToken(user, user_token):
    """check user login token is save as user id's token"""
    if not user or not user_token:
        return False
    return user_token == generateUserToken(user)


def addCookieLogin(response, user):
    """add login info into cookie"""
    expire_time = 60 * 60 * 24 * 180  # half year
    user_token = generateUserToken(user)
    response.set_cookie('user_id', user.id, max_age=expire_time)
    response.set_cookie('user_token', user_token, max_age=expire_time)
    return response


def getCookieLogin(request):
    """将 cookie 中存的 user 信息存入 session 并返回"""
    user_id = request.COOKIES.get('user_id')
    user_token = request.COOKIES.get('user_token')
    if not user_id or not user_token:
        return None
    user = User.objects.get_or_none(id=user_id)
    if user and checkUserToken(user, user_token):
        rememberLogin(request, user)
        return user
    return None


def getRandomName():
    """Generate user nickname"""
    shengmu = ['a', 'i', 'u', 'e', 'o']
    yunmu = ['s', 'k', 'm', 'n', 'r', 'g', 'h', 'p', 'b', 'z', 't', 'd']
    nickname = random.choice(yunmu).upper() + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu) + random.choice(yunmu) + random.choice(shengmu)
    users = User.objects.filter(nickname=nickname)
    if len(users) > 0:
        return getRandomName()
    return nickname


def loginToContinue(request):
    """Show a message, goto login page, and then go back to current page"""
    messages.error(request, _('此页面需要用户信息，\n请登录/注册后再访问。'))
    _from = request.get_full_path()
    return redirect('/user/signin?next={}'.format(_from))


def login_required(func):
    """Decorator. If not logged in, goto login page. Should be on the top of decorators"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = getCurrentUser(request)
        if not user:
            return util.user.loginToContinue(request)
        return func(request, *args, **kwargs)
    return wrapper


def superuser_required(func):
    """Decorator. If logged in but not superuser, block."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = getCurrentUser(request)
        if not user.getUserpermission('superuser'):
            return util.ctrl.infoMsg(_("您不具有{}权限").format(_("超级管理员")))
        return func(request, *args, **kwargs)
    return wrapper
