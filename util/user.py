from main.models import User
from django.contrib import messages
from django.shortcuts import redirect


def getCurrentUser(request):
    """Get logined user from session"""
    userid = request.session.get(User.LOGIN_SESSION_KEY)
    if not userid:
        return False
    try:
        user = User.objects.get(id=userid)
    except User.DoesNotExist:
        return None
    return user


def rememberLogin(request, user):
    """Remember logined user"""
    if not user:
        return None
    request.session[User.LOGIN_SESSION_KEY] = user.id  # remember login
    return True


def loginToContinue(request):
    """Show a message, goto login page, and then go back to current page"""
    messages.error(request, '此页面需要用户信息，\n请登入/注册后再访问。')
    _from = request.get_full_path()
    return redirect('/user/signin?from={}'.format(_from))
