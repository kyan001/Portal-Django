from django.shortcuts import render, redirect
import util.ctrl
import util.user
import util.userexp
import random


def index(request):
    context = {}
    if util.ctrl.isMobile(request):
        return render(request, 'index/index-m.html', context)
    return render(request, 'index/index.html', context)


@util.user.login_required
def settheme(request):
    '''保存/清除用户的 theme 到 cookies 里'''
    # get history.back
    if 'HTTP_REFERER' in request.META:
        href_back = request.META.get('HTTP_REFERER')
        response = redirect(href_back)
    else:
        response = redirect('/')
    # CONSTANTS
    theme_name_pool = ("cerulean", "cosmo", "cyborg", "darkly", "flatly", "journal", "lumen", "paper", "readable", "sandstone", "simplex", "slate", "spacelab", "superhero", "united", "yeti")
    theme_key = 'theme'
    # get input
    theme_name = request.GET.get('name')
    mode = request.GET.get('mode')
    if mode == 'random':  # 随机主题
        theme_name = random.choice(theme_name_pool)
    if not theme_name:  # 清除已设置的主题
        response.delete_cookie(theme_key)
    else:  # 设置主题
        theme_name = theme_name.lower()
        if theme_name not in theme_name_pool:
            return util.ctrl.infoMsg("您请求的主题：{theme_name} 不存在".format(theme_name=theme_name), title="设置主题失败")
        oneweek = 60 * 60 * 24 * 7
        response.set_cookie(theme_key, theme_name, max_age=oneweek)
    # add exp
    user = util.user.getCurrentUser(request)
    theme_name_smart = theme_name or '默认主题'
    util.userexp.addExp(user, 'user', 2, '尝试主题：{theme_name}'.format(theme_name=theme_name_smart.title()))
    return response


def help(request):  # GET
    """网站的帮助页"""
    return redirect('//readthedocs.org')
