import json
import urllib.request
import re
import datetime

from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone
from main.models import UserExp

import util.ctrl


def robotalkIndex(request):
    context = {}
    user = util.user.getCurrentUser(request)
    if user:
        userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
        userexp.addExp(1, '与 RoboTalk 对话')
    # save/get counter start time
    cache_key = 'robotalk:starttime'
    cache_timeout = 60 * 60 * 24 * 7 * 4  # 1 month
    cache_starttime = cache.get(cache_key)
    if not cache_starttime:
        cache_starttime = timezone.now()
        cache.set(cache_key, cache_starttime, cache_timeout)
    context['starttime'] = str(timezone.now() - cache_starttime)
    return render(request, 'robotalk/index.html', context)


def robotalkGetresponse(request):  # AJAX
    """Get input and take back request via AJAX"""
    userinput = request.GET.get('txt')
    if not userinput:
        return util.ctrl.returnJsonError('userinput is empty')
    from_ = request.GET.get('from')
    # save count into cache
    cache_key = 'robotalk:count'
    cache_timeout = 60 * 60 * 24 * 7 * 4  # 1 month
    cache_count = cache.get(cache_key, 0)
    cache_count += 1
    cache.set(cache_key, cache_count, cache_timeout)

    def getFullurl(robo):
        if not (robo and robo.get('param') and robo.get('url')):
            return None
        param = urllib.parse.urlencode(robo.get('param'))
        fullurl = "{u}?{p}".format(u=robo.get('url'), p=param)
        return fullurl

    def getResponse(robo):
        fullurl = getFullurl(robo)
        u = urllib.request.urlopen(fullurl)
        u_resp = u.read()
        if not u_resp:
            return None
        resp_str = u_resp.decode()
        return robo.get('getContent')(resp_str)

    def addToResult(robo, result):
        key = robo.get('from')
        time_now = datetime.datetime.now()
        value = {
            'txt': getResponse(robo),
            'fullurl': getFullurl(robo),
        }
        time_rtt = (datetime.datetime.now() - time_now).microseconds / 1000
        value['rtt'] = int(time_rtt)  # milliseconds
        result['result'][key] = value
        return True

    def extractFeifei(content: str):
        """从 菲菲 的返回字符串中获得真正的内容"""
        if not content:
            return None
        json_obj = json.loads(content)
        content = json_obj.get('content').replace('{br}', '<br/>')
        content = re.sub(r'{face:[0-9]+}', '', content)
        return content

    def extractSimsimi(content: str):
        """从 Simsimi 的返回字符串中获得真正的内容"""
        if not content:
            return None
        content = content.replace('\n', '<br/>')
        return content
    # robos list(dictionary)
    robos = {
        'simsimi': {
            'from': 'simsimi',
            'url': 'http://www.xiaodoubi.com/simsimiapi.php',
            'param': {'msg': userinput},
            'getContent': extractSimsimi,
        },
        'feifei': {
            'from': 'feifei',
            'url': 'http://api.qingyunke.com/api.php',
            'param': {
                'key': 'free',
                'appid': 0,
                'msg': userinput,
            },
            'getContent': extractFeifei,
        },
    }
    # get results
    result = {'result': {}}
    if from_:
        robo = robos.get(from_)
        addToResult(robo, result)
    else:
        for i in robos:
            addToResult(robos.get(i), result)
    # render
    result['count'] = cache_count
    return util.ctrl.returnJson(result)
