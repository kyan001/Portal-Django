import util.ctrl
from django import template
register = template.Library()


@register.filter
def isurl(url):
    return util.ctrl.isUrl(url)
