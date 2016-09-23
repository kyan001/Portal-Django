from main.models import User


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
