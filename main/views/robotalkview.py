import json
import urllib.request

from django.shortcuts import render_to_response
from django.core.cache import cache
from django.utils import timezone
from main.models import User, UserExp

import util.ctrl


def robotalkIndex(request):
    context = {'request': request}
    current_user = request.session.get('loginuser')
    if current_user:
        try:
            user = User.objects.get(id=current_user['id'])
        except User.DoesNotExist:
            return util.ctrl.infoMsg("您查找的用户 id：{id} 并不存在".format(id=current_user['id']))
        userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
        userexp.addExp(1, '与 RoboTalk 对话')
    # save/get counter start time
    cache_key = 'robotalk:starttime'
    cache_timeout = 60 * 60 * 24 * 7 * 4  # 1 month
    cache_starttime = cache.get(cache_key)
    if not cache_starttime:
        cache_starttime = timezone.now()
        cache.set(cache_key, cache_starttime, cache_timeout)
    context['starttime'] = str(cache_starttime - timezone.now())
    return render_to_response('robotalk/index.html', context)


def robotalkGetresponse(request):  # AJAX
    """Get input and take back request via AJAX"""
    userinput = request.GET.get('txt')
    if not userinput:
        return util.ctrl.returnJsonError('userinput is empty')
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
        return u_resp.decode()
    robo1 = {
        'url': 'http://www.niurenqushi.com/app/simsimi/ajax.aspx',
        'param': {'txt': userinput},
        'from': 'simsimi',
    }
    robo2 = {
        'url': 'http://api.qingyunke.com/api.php',
        'param': {
            'key': 'free',
            'appid': 0,
            'msg': userinput,
        },
        'from': 'feifei',
    }
    robo1_says = getResponse(robo1)
    robo2_resp = getResponse(robo2)
    robo2_says = json.loads(robo2_resp).get('content').replace('{br}', '<br/>')
    result = {
        'result': {
            robo1.get('from'): {
                'txt': robo1_says,
                'fullurl': getFullurl(robo1),
            },
            robo2.get('from'): {
                'txt': robo2_says,
                'fullurl': getFullurl(robo2),
            },
        },
        'count': cache_count
    }
    return util.ctrl.returnJson(result)
