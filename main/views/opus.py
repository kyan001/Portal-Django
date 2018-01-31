import io
import json
import urllib.request
import urllib.parse

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import gettext as _
import jieba
import wordcloud

from main.models import Opus
import util.ctrl


def detail(request):
    """获得作品的详情"""
    opusid = request.GET.get('id')
    if not opusid:
        raise Http404(_("{} 参数不能为空").format("Opus ID"))
    # get opus
    opus = Opus.objects.get_or_404(id=opusid)
    # render
    context = {
        'opus': opus,
    }
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
        param = {
            'count': count,
            'q': keyword,
        }
        param_encoded = urllib.parse.urlencode(param)
        url_final = url + '?' + param_encoded  # ?count=1&q=xxx
        response = urllib.request.urlopen(url_final)
        info = response.read()
        cache.set(cache_key, info, cache_timeout)
    return HttpResponse(info, content_type='application/json')


def generateWordCloud(txt, height=500, width=500):
    """从 txt 获得词云，返回 png 图片"""
    seg_list = jieba.cut(txt, cut_all=False)
    seg_str = " ".join(seg_list)
    cloud = wordcloud.WordCloud(relative_scaling=0.5, scale=1.5, width=int(width / 1.5), height=int(height / 1.5), font_path="static/fonts/SourceHanSansSC-Medium.otf", background_color=None, mode='RGBA').generate(seg_str)
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

    opus_name = request.GET.get('name')  # 用户存的名字.
    opus_type = request.GET.get('type')
    height = request.GET.get('height') or "500"
    width = request.GET.get('width') or "500"
    if not (opus_name and opus_type):
        raise Http404(_("{} 参数不能为空").format("Opus Name" + _("和") + "Opus Type"))
    info = getOpusCachedInfo(opus_type, opus_name)
    if not info:
        raise Http404(_("{} 未被缓存").format("Opus Info"))
    # check cached
    cache_key = '{typ}:{name}:{hght}x{wdth}:wordcloud'.format(typ=opus_type, name=opus_name, hght=height, wdth=width)
    cache_timeout = 60 * 60 * 24 * 30 * 2  # 2 months
    cached_data = cache.get(cache_key)
    if cached_data:
        buf = io.BytesIO(cached_data)
        wrdcld_img = buf.getvalue()
        buf.close()
    else:
        summary = info['books'][0]['summary']
        wrdcld_img = generateWordCloud(summary, width=int(width), height=int(height))
        cache.set(cache_key, wrdcld_img, cache_timeout)
    # render
    response = HttpResponse(wrdcld_img, content_type='image/png')
    return response


@util.user.login_required
def importFrom(request):
    """将别人的进度导入至自己的进度列表

    Args:
        id: str，作为被导入的 opus id
    """
    opusid = request.GET.get('id')
    if not opusid:
        return util.ctrl.infoMsg(_("{} 参数不能为空").format("Opus ID"))
    user = util.user.getCurrentUser(request)
    opus = Opus.objects.get_or_404(id=int(opusid))  # 获得作品.
    if opus.progress.userid == user.id:  # 判断是否是自己的进度.
        return util.ctrl.infoMsg(_("您已拥有该进度，请不要重复添加"), title=_('导入失败'))
    # 生成 url
    url = '/progress/new'
    param = {
        'name': opus.name,
        'total': opus.total,
        'weblink': opus.progress.weblink,
    }
    param_encoded = urllib.parse.urlencode(param)
    url_final = url + '?' + param_encoded  # ?name=xxx&total=xxx&weblink=xxx
    messages.success(request, _("已从 @{u} 导入进度《{o}》的信息").format(u=user.nickname, o=opus.name))
    messages.warning(request, _("请确认后点击“保存”"))
    return redirect(url_final)
