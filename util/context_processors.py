import util.user


def loggedUser(request):
    """Add logged user to context

    Args:
        request: Django HttpRequest object
    Returns:
        cuser: current user
    """
    return {'cuser': util.user.getCurrentUser(request)}
