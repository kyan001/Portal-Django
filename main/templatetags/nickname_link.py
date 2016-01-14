from main.models import User
from django import template
import re
register = template.Library()

@register.filter
def extractnickname(text):
    if not isinstance(text, str):
        return text
    final_set = set()
    nickname_pattern = re.compile(r'@([\S]+)')
    nickname_list = nickname_pattern.findall(text)
    for nn in nickname_list:
        try:
            user = User.objects.get(nickname=nn)
        except User.DoesNotExist:
            final_set.add("<del class='text-muted'>@{}</del>".format(nn))
            break
        final_set.add('<a href="/user/public?nickname={nickname}">@{nickname}</a>'.format(nickname=nn))
    return final_set

