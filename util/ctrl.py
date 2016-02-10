from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings
from django.utils import timezone
import random

import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        'title':title,
        'content':content,
        'url':url,
    }
    if url:
        if url == '/':
            button_text = '回到主页'
        elif '/user/signin' in url:
            button_text = '前往「登入」页面'
        elif '/user/signup' in url:
            button_text = '前往「注册」页面'
        elif '/progress/list' in url:
            button_text = '前往「我的进度-列表」页面'
        else:
            button_text = None
        context['button'] = button_text
    return render_to_response("msg.html", context);

def returnJson(dict_input):
    if dict_input:
        #return HttpResponse(json.dumps(dict_input), content_type='application/json')
        return JsonResponse(dict_input);
    else:
        return JsonResponse({'error':'returnJson() input dict_input is empty'})

def returnJsonError(word):
    if word:
        return returnJson({'error':word});
    else:
        return returnJson({'error':"input of returnJsonError() is empty"})

def returnJsonResult(word):
    if word:
        return returnJson({'result':word});
    else:
        return returnJson({'result':"input of returnJsonResult() is empty"})

def salty(word):
    word_in_str = str(word)
    word_with_suffix = word_in_str + "superfarmer.net"
    return ktk.md5(word_with_suffix)

def calcLevel(exp):
    if isinstance(exp, int):
        return int(exp**0.5)
    return None

def calcExp(level):
    if isinstance(level, int):
        return int(level**2)
    return None

def needLogin():
    return infoMsg("此页面需要用户信息，\n请登入/注册后再访问。", url="/user/signin", title="请先登入")
    # return redirect('/user/signin');

def sendEmail(word, to_email, subject='一封来自SuperFarmer网站的邮件'):
    if not word:
        return False;
    if not to_email or to_email.find('@') <= 0:
        return False;
    subject = subject
    content = loader.render_to_string('email.html', {'subject':subject.strip(), 'content':word.strip()})
    msg = EmailMessage(
        subject.strip()+' - superfarmer.net', #subject
        content, #content
        settings.EMAIL_HOST_USER, #from email
        [settings.EMAIL_HOST_USER, to_email.strip()] #recipients
        )
    msg.content_subtype = 'html'
    msg.send()
    return True

def formatDate(dt, mode="optimize"):
    if mode == 'optimize': #[2015-]12-05 11:25 am
        time_format = '%m-%d %H:%M %p'
        if dt.year != timezone.now().year:
            time_format = '%Y-' + time_format
    elif mode == 'dateonly': #12-05
        time_format = '%m-%d';
    elif mode == 'fulldateonly': #2015-12-05
        time_format = '%Y-%m-%d';
    elif mode == 'timeonly':
        time_format = '%H:%M:%S'
    else:
        time_format = '%Y-%m-%d %H:%M %p'
    return dt.astimezone(timezone.get_current_timezone()).strftime(time_format)

def formatTimedelta(td, mode="full"):
    # get data
    d = td.days
    h = td.seconds // (60*60)
    m = td.seconds % (60*60) // 60
    s = td.seconds % 60
    days = '{d}天'.format(d=d)
    hours = '{h}小时'.format(h=h)
    minutes = '{m}分'.format(m=m)
    seconds = '{s}秒'.format(s=s)
    # parse mode
    if mode == 'full': #1天 11小时 7分 22秒
        mode = '%d %H %M %S'
    result = mode
    result = result.replace('%d', days if d else '').replace('%H', hours).replace('%M', minutes).replace('%S', seconds).strip()
    # return
    if not result:
        result = str(td)
    return result
