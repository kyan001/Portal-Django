import json
import urllib.request
import re
import datetime

from django.shortcuts import render
from django.core.cache import cache
from django.utils import timezone
from main.models import UserExp

import util.ctrl


def index(request):
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


def getResponse(request):  # AJAX
    """Get input and take back request via AJAX"""
    userinput = request.GET.get('txt')
    if not userinput:
        return util.ctrl.returnJsonError('userinput is empty')
    from_ = request.GET.get('from')

    # extracts
    def extractFeifei(content: str):
        """从 feifei 的返回字符串中获得真正的内容"""
        if not content:
            return None
        json_obj = json.loads(content)
        content = json_obj.get('content')
        if content:
            content.replace('{br}', '<br/>')
            content = re.sub(r'{face:[0-9]+}', '', content)
        return content

    def extractSimsimi(content: str):
        """从 Simsimi 的返回字符串中获得真正的内容"""
        if not content:
            return None
        json_obj = json.loads(content)
        content = json_obj.get('response')
        if content:
            content.replace('{br}', '<br/>')
        return content

    def extractProgramo(content: str):
        """从 Program-O 的返回字符串中获得真正的内容"""
        if not content:
            return None
        json_obj = json.loads(content)
        content = json_obj.get('botsay')
        return content

    def extractTuling(content: str):
        """从 Tuling 的返回字符串中获得真正的内容"""
        if not content:
            return None
        json_obj = json.loads(content)
        content = json_obj.get('text')
        if content:
            content.replace('{br}', '<br/>')
        return content

    # ROBOS list(dictionary)
    ROBOS = {
        'simsimi': {
            'from': 'simsimi',
            'url': 'http://sandbox.api.simsimi.com/request.p',
            'param': {
                'key': '434daf7b-e657-4192-8fb9-ba38bfa5f730',
                'lc': 'zh',
                'ft': '1.0',
                'text': userinput,
            },
            'getContent': extractSimsimi,
            'disabled': True,
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
        'tuling': {
            'from': 'tuling',
            'url': 'http://www.tuling123.com/openapi/api',
            'param': {
                'key': '96dd75c1bfb64b2094327ba286da25d6',
                'info': userinput,
            },
            'getContent': extractTuling,
        },
        'programo': {
            'from': 'programo',
            'url': 'http://api.program-o.com/v2/chatbot/',
            'param': {
                'format': 'json',
                'bot_id': '6',
                'convo_id': request.session.session_key[0:6],  # first 6 digits of session_key as the conversation identifier
                'say': userinput,
            },
            'getContent': extractProgramo,
            'disabled': True,
        },
    }

    # save count into cache
    def getTotalMessageCounts():
        """服务器启动后一共进行过多少次对话"""
        cache_key = 'robotalk:count'
        cache_timeout = 60 * 60 * 24 * 7 * 4  # 1 month
        cache_count = cache.get(cache_key, 0)
        cache_count += 1
        cache.set(cache_key, cache_count, cache_timeout)
        return cache_count

    def getFullurl(robo):
        """根据每个 robo 的参数和地址生成完整的字符串请求 url"""
        if not (robo and robo.get('param') and robo.get('url')):
            return None
        param = urllib.parse.urlencode(robo.get('param'))
        fullurl = "{u}?{p}".format(u=robo.get('url'), p=param)
        return fullurl

    def getRoboResponse(robo):
        """获得某个 robo 的回复

        Args:
            robo: ROBOS[i]
        """
        fullurl = getFullurl(robo)
        u = urllib.request.urlopen(fullurl)
        u_resp = u.read()
        if not u_resp:
            return None
        return u_resp.decode()

    def addResponseToResult(robo, r):
        """将某个 robo 的回复及元数据加入到结果集中

        Args:
            robo: ROBOS[i]
            r: RESULT, which will be modified
        """
        key = robo.get('from')
        time_now = datetime.datetime.now()
        resp = getRoboResponse(robo)
        txt = robo.get('getContent')(resp)
        time_rtt = int((datetime.datetime.now() - time_now).microseconds / 1000)  # milliseconds
        value = {
            'txt': txt,
            'fullurl': getFullurl(robo),
            'response': resp,
            'rtt': time_rtt,
        }
        if not txt:
            r['failed'][key] = value
        else:
            r['result'][key] = value

    def addDisabledToResult(robo, r):
        """将已禁用的 robo 加入到结果集中

        Args:
            robo: ROBOS[i]
            r: RESULT, which will be modified
        """
        key = robo.get('from')
        time_now = datetime.datetime.now()
        r['disabled'][key] = {
            'time': time_now,  # not necessary
        }

    # get results
    RESULT = {
        'result': {},  # 可用的结果，Available results
        'failed': {},  # 发送了请求但未返回内容的，responsed but no txt
        'disabled': {},  # 不可用的，force to not request
        'count': getTotalMessageCounts(),  # 对话总数，message number from cache
    }
    if from_:
        robo = ROBOS.get(from_)
        addResponseToResult(robo, RESULT)
    else:
        for i in ROBOS:
            robo = ROBOS.get(i)
            if robo.get('disabled'):  # disabled 的机器人加入结果的 disabled 中
                addDisabledToResult(robo, RESULT)
            else:  # 未 disabled 的加入结果的 result 或 failed 中
                addResponseToResult(robo, RESULT)
    # render
    return util.ctrl.returnJson(RESULT)
