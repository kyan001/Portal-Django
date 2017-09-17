import io
import json
import urllib.request
import urllib.parse
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
import jieba
import wordcloud

from main.models import Opus
import util.ctrl


def detail(request):
    '''获得作品的详情'''
    context = {}
    # 获得参数
    opusid = request.GET.get('id')
    if not opusid:
        return util.ctrl.infoMsg("需要一个作品id")
    # 获得作品
    opus = Opus.objects.get_or_404(id=opusid)
    # 获得进度列表
    opus_list = Opus.objects.filter(name=opus.name)
    item_list = [{'progress': opuslet.progress, 'user': opuslet.progress.user, 'opus': opuslet} for opuslet in opus_list]
    # render
    context['opus'] = opus
    context['itemlist'] = item_list
    return render(request, 'opus/detail.html', context)


def searchOpusInfo(request):  # get # ajax
    """从豆瓣获取书类作品信息并放入缓存"""
    opustype = request.GET.get('type') or 'book'
    count = request.GET.get('count') or '1'
    keyword = request.GET.get('q')
    cache_key = '{typ}:{kw}:info'.format(typ=opustype, kw=keyword.replace(' ', '_'))
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


def generateWordCloud(txt, height=500, width=500):
    """从 txt 获得词云，返回 png 图片"""
    seg_list = jieba.cut(txt, cut_all=False)
    seg_str = " ".join(seg_list)
    cloud = wordcloud.WordCloud(relative_scaling=0.5, scale=1.5, width=int(width/1.5), height=int(height/1.5), font_path="static/fonts/SourceHanSansSC-Medium.otf", background_color=None, mode='RGBA').generate(seg_str)
    cloud_image = cloud.to_image()  # or cloud.to_file(path)
    # save to cache
    buf = io.BytesIO()
    cloud_image.save(buf, 'png')
    wrdcld_img = buf.getvalue()
    buf.close()
    return wrdcld_img


@csrf_exempt
def getOpusWordCloud(request):  # get # ajax
    """从 opus 的 summary 获得词云，返回 png 图片"""
    def getOpusCachedInfo(opustype, keyword):
        cache_key = '{typ}:{kw}:info'.format(typ=opustype, kw=keyword.replace(' ', '_'))
        cached_info = cache.get(cache_key)
        if type(cached_info) == bytes:
            cached_info = cached_info.decode()
        return json.loads(cached_info) if cached_info else None

    opus_name = request.GET.get('name')
    opus_type = request.GET.get('type')
    height = request.GET.get('height') or "500"
    width = request.GET.get('width') or "500"
    if not (opus_name and opus_type):
        raise Http404("opus 的参数 name 和 opustype 不能为空")
    # check cached
    cache_key = '{typ}:{name}:{hght}x{wdth}:wordcloud'.format(typ=opus_type, name=opus_name, hght=height, wdth=width)
    cache_timeout = 60 * 60 * 24 * 30 * 2  # 2 months
    cached_data = None; cache.get(cache_key)
    if cached_data:
        buf = io.BytesIO(cached_data)
        wrdcld_img = buf.getvalue()
        buf.close()
    else:
        info = getOpusCachedInfo(opus_type, opus_name)
        if not info:
            raise Http404("opus 的 info 不存在")
        summary = info['books'][0]['summary']
        wrdcld_img = generateWordCloud(summary, width=int(width), height=int(height))
        cache.set(cache_key, wrdcld_img, cache_timeout)
    # render
    response = HttpResponse(wrdcld_img, content_type='image/png')
    return response
