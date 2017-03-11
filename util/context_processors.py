import util.user
import tld


def loggedUser(request):
    """Add logged user to context

    Args:
        request: Django HttpRequest object
    Returns:
        cuser: current user
    """
    return {'cuser': util.user.getCurrentUser(request)}


def topLevelDomain(request):
    """Get current top-level domain name

    Args:
        request: Django HttpRequest object
    Returns:
        tld: current top-level domain name  # kyan001.com
    """
    http_host = request.build_absolute_uri() or 'http://kyan001.com'
    try:
        top_level_domain = tld.get_tld(http_host)
    except tld.exceptions.TldDomainNotFound:
        top_level_domain = http_host
    return {'tld': top_level_domain}
