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


def firstLevelDomain(request):
    """Get current first-level domain

    Args:
        request: Django HttpRequest object
    Returns:
        fld: current first-level domain name  # kyan001.com
    """
    http_host = request.build_absolute_uri() or 'http://kyan001.com'
    try:
        first_level_domain = tld.get_fld(http_host)
    except tld.exceptions.TldDomainNotFound:
        first_level_domain = http_host
    return {'fld': first_level_domain}
