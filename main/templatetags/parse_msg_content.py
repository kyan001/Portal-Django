from main.models import User
from django import template
import re
register = template.Library()
nickname_url = '<a class="text-primary" href="/user/public?nickname={nickname}">@{nickname}</a>'
topic_url = '<a class="text-info" href="https://www.baidu.com/s?wd={topic}" target="_blank">#{topic}</a>'

@register.filter
def extractlink(text):
    if not isinstance(text, str):
        return text
    # extrace nicknames
    final_set = set()
    nickname_pattern = re.compile(r'@([\S]+)')
    nickname_list = nickname_pattern.findall(text)
    for nn in nickname_list:
        try:
            user = User.objects.get(nickname=nn)
            final_set.add(nickname_url.format(nickname=user.nickname))
        except User.DoesNotExist:
            final_set.add("<del class='text-muted'>@{}</del>".format(nn))
    # extract topics
    topic_pattern = re.compile(r'#([\S]+)')
    topic_list = topic_pattern.findall(text)
    for tp in topic_list:
        final_set.add(topic_url.format(topic=tp))
    return final_set

@register.filter
def highlightlink(text):
    if not isinstance(text, str):
        return text
    # highlight nicknames
    nickname_pattern = re.compile(r'@([\S]+)')
    nickname_list = nickname_pattern.findall(text)
    for nn in nickname_list:
        try:
            user = User.objects.get(nickname=nn)
            text = text.replace("@{}".format(nn), nickname_url.format(nickname=nn))
        except User.DoesNotExist:
            text = text.replace("@{}".format(nn), "<del class='text-muted'>@{}</del>".format(nn))
    # highlight topics
    topic_pattern = re.compile(r'#([\S]+)')
    topic_list = topic_pattern.findall(text)
    for tp in topic_list:
        text = text.replace('#{}'.format(tp), topic_url.format(topic=tp))
    return text.replace('\n','<br/>')
