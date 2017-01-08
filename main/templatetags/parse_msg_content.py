from main.models import User
from django import template
import re
register = template.Library()
nickname_url = '<a class="text-primary" href="/user/public?nickname={nickname}">@{nickname}</a>'
topic_url = '<a class="text-info" href="https://www.baidu.com/s?wd={topic}" target="_blank">#{topic}</a>'


def findNickname(text):
    pattern = re.compile(r'@([\S]+)')
    return pattern.findall(text)


def findTopic(text):
    pattern = re.compile(r'#([\S]+)')
    return pattern.findall(text)


@register.filter
def extractlink(text):
    if not isinstance(text, str):
        return text
    # extrace nicknames
    final_set = set()
    for nn in findNickname(text):
        if '.com' in nn:
            continue
        elif User.objects.filter(nickname=nn).exists() and '.com' not in nn:
            final_set.add(nickname_url.format(nickname=nn))
        else:
            final_set.add("<del class='text-muted'>@{}</del>".format(nn))
    # extract topics
    for tp in findTopic(text):
        final_set.add(topic_url.format(topic=tp))
    return final_set


@register.filter
def highlightlink(text, mode='default'):
    if not isinstance(text, str):
        return text
    # highlight nicknames
    for nn in findNickname(text):
        if '.com' in nn:
            continue
        elif User.objects.filter(nickname=nn).exists():
            text = text.replace("@{}".format(nn), nickname_url.format(nickname=nn))
        else:
            text = text.replace("@{}".format(nn), "<del class='text-muted'>@{}</del>".format(nn))
    # highlight topics
    for tp in findTopic(text):
        text = text.replace('#{}'.format(tp), topic_url.format(topic=tp))
    if mode != 'sys':
        text = text.replace('\n', '<br/>')
    return text
