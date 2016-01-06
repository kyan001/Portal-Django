from django.shortcuts import render_to_response, redirect
from util.ctrl import *

# Create your views here.
def index(request):
    context = {'request': request}
    return render_to_response('index/index.html', context);

def indexSettheme(request):
    '''保存用户的 theme 到 cookies 里'''
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
    if not theme_name: # 清除已设置的皮肤
        response.delete_cookie(theme_key)
        return response
    # validate theme name & set theme
    theme_name = theme_name.lower()
    if theme_name not in theme_name_pool:
        return infoMsg("您请求的主题：{0} 不存在".format(theme_name), title="设置主题失败")
    oneweek = 60*60*24*7
    response.set_cookie(theme_key, theme_name, max_age=oneweek)
    return response
