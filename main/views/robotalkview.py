import json
import urllib.request
from django.shortcuts import render_to_response
from django.http import JsonResponse


def robotalkIndex(request):
    context = {'request': request}
    current_user = request.session.get('loginuser');
    return render_to_response('robotalk/index.html', context)


def robotalkGetresponse(request):  # AJAX
    """Get input and take back request via AJAX"""
    userinput = request.GET.get('txt')
    if not userinput:
        return JsonResponse({'error': 'userinput is empty'})

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
    }
    return JsonResponse(result)
