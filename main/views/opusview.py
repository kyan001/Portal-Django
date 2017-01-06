from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
import urllib.request
import urllib.parse
from main.models import Opus, Progress, User
import util.ctrl

import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


def opusDetail(request):
    '''TODO 获得作品的详情'''
    context = {}
    # 获得参数
    opusid = request.GET.get('id')
    if not opusid:
        return util.ctrl.infoMsg("需要一个作品id")
    # 获得作品
    try:
        opus = Opus.objects.get(id=opusid)
    except Opus.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的作品".format(id=str(opusid)))
    # 获得进度列表
    opus_list = Opus.objects.filter(name=opus.name)
    item_list = []
    for opuslet in opus_list:
        # 获得进度
        try:
            progress = opuslet.progress
        except Progress.DoesNotExist:
            return util.ctrl.infoMsg("未找到 opusid 为 {id} 的进度".format(id=str(opusid)))
        # 获得用户
        try:
            user = progress.user
        except User.DoesNotExist:
            return util.ctrl.infoMsg("未找到 id 为 {progress.userid} 的进度".format(progress=progress))
        item_list.append({'progress': progress, 'user': user, 'opus': opuslet})
    # render
    context['opus'] = opus
    context['itemlist'] = item_list
    return render(request, 'opus/detail.html', context)

def opusSearchOpusInfo(request):  # get # ajax
    """从豆瓣获取书类作品信息并放入缓存"""
    opustype = request.GET.get('type') or 'book'
    count = request.GET.get('count') or '1'
    keyword = request.GET.get('q')
    cache_key = '{typ}:{kw}:info'.format(typ=opustype, kw=keyword.replace(' ','_'))
    cache_timeout = 60 * 60 * 24 * 7 * 2  # 2 weeks
    cached_info = cache.get(cache_key)
    if cached_info:
        info = cached_info
    else:
        if opustype == 'movie':
            url = 'https://api.douban.com/v2/movie/search'
        elif opustype == 'book':
            url = 'https://api.douban.com/v2/book/search'
        else:
            raise Exception('Wrong opus type')
        url += '?count={cnt}&q={kw}'.format(cnt=count, kw=urllib.parse.quote(keyword))
        response = urllib.request.urlopen(url)
        info = response.read()
        cache.set(cache_key, info, cache_timeout)
    return HttpResponse(info, content_type='application/json')
