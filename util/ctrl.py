from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings
from django.utils.translation import gettext as _

import KyanToolKit as ktk


# Utils
def infoMsg(content="Hi", url=None, title=None):
    context = {
        "title": title,
        "content": content,
        "url": url,
    }
    if url:
        if url == "/":
            button_text = _("回到主页")
        elif "/user/signin" in url:
            button_text = _("前往「{}」页面").format(_("登入"))
        elif "/user/signup" in url:
            button_text = _("前往「{}」页面").format(_("注册"))
        elif "/progress/list" in url:
            button_text = _("前往「{}」页面").format(_("进度列表"))
        elif "/chat/inbox" in url:
            button_text = _("前往「{}」页面").format(_("收信箱"))
        elif "/chat/quicknote" in url:
            button_text = _("前往「{}」页面").format(_("临时笔记"))
        else:
            button_text = None
        context["button"] = button_text
    return render(None, "msg.html", context)


def returnJson(dict_input):
    if dict_input:
        # return HttpResponse(json.dumps(dict_input), content_type='application/json')
        return JsonResponse(dict_input)
    else:
        return JsonResponse({'error': 'returnJson() input dict_input is empty'})


def returnJsonError(word):
    if word:
        return returnJson({'error': word})
    else:
        return returnJson({'error': "input of returnJsonError() is empty"})


def returnJsonResult(word):
    if word:
        return returnJson({'result': word})
    else:
        return returnJson({'result': "input of returnJsonResult() is empty"})


def salty(word):
    word_in_str = str(word)
    word_with_suffix = word_in_str + "superfarmer.net"
    return ktk.KyanToolKit.md5(word_with_suffix)


def calcLevel(exp):
    if isinstance(exp, int):
        return int(exp**0.5)
    return None


def calcExp(level):
    if isinstance(level, int):
        return int(level**2)
    return None


def sendEmail(word, to_email, subject="重要邮件"):
    if not word:
        return False
    if not to_email or to_email.find('@') <= 0:
        return False
    content = loader.render_to_string('email.html', {
        'subject': subject.strip(),
        'content': word.strip(),
    })
    msg = EmailMessage(
        subject.strip() + "kyan001.com",  # subject
        content,  # content
        settings.EMAIL_HOST_USER,  # from email
        [settings.EMAIL_HOST_USER, to_email.strip()]  # recipients
    )
    msg.content_subtype = 'html'
    msg.send()
    return True


def isMobile(request):
    if not request:
        return False
    user_agent = request.META.get('HTTP_USER_AGENT')
    if not user_agent:
        return False
    if user_agent.lower().find('mobile') < 0:
        return False
    return True


def isUrl(url):
    return "://" in str(url)
