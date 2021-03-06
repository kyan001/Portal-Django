import io
import json
import urllib.request
import urllib.parse

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.cache import cache
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import gettext as _
import jieba
import wordcloud

from main.models import Progress
import util.ctrl


def detail(request):
    """获得作品的详情"""
    progressid = request.GET.get('progressid')
    if not progressid:
        raise Http404(_("{} 参数不能为空").format("Progress ID"))
    # get progress
    progress = Progress.objects.get_or_404(id=progressid)
    # render
    context = {
        'progress': progress,
    }
    return render(request, 'opus/detail.html', context)


def searchOpusInfo(request):  # get # ajax
    """从豆瓣获取书类作品信息并放入缓存"""
    opustype = request.GET.get('type') or 'book'
    count = request.GET.get('count') or '1'
    keyword = request.GET.get('q')
    cache_key = '{typ}:{kw}:info'.format(typ=opustype, kw=keyword.replace(' ', '_'))
    cache_timeout = 60 * 60 * 24 * 7 * 2  # 2 weeks
    cached_resp = cache.get(cache_key)
    if cached_resp:
        http_resp = cached_resp
    else:
        if opustype == 'movie':
            url = 'https://douban.uieee.com/v2/movie/search'  # 'https://api.douban.com/v2/movie/search'
        elif opustype == 'book':
            url = 'https://douban.uieee.com/v2/book/search'  # 'https://api.douban.com/v2/book/search'
        else:
            raise Http404('Wrong opus type')
        param = {
            'count': count,
            'q': keyword,
        }
        param_encoded = urllib.parse.urlencode(param)
        url_final = url + '?' + param_encoded  # ?count=1&q=xxx
        try:
            response = urllib.request.urlopen(url_final)
        except urllib.error.HTTPError as err:
            raise Http404("ERROR: {err}, API_URL: {err.url}".format(err=err))
        info = response.read()
        http_resp = {
            "meta": {
                "opustype": opustype,
                "api": url_final
            },
            "data": json.loads(info)
        }
        cache.set(cache_key, http_resp, cache_timeout)
    return JsonResponse(http_resp)


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
        return cached_info.get('data') if cached_info else None

    opusname = request.GET.get('name')  # 用户存的名字.
    opustype = request.GET.get('type')
    height = request.GET.get('height') or "500"
    width = request.GET.get('width') or "500"
    if not (opusname and opustype):
        raise Http404(_("{} 参数不能为空").format("Opus Name" + _("和") + "Opus Type"))
    info = getOpusCachedInfo(opustype, opusname)
    if not info:
        raise Http404(_("{} 未被缓存").format("Opus Info"))
    # check cached
    cache_key = '{typ}:{name}:{hght}x{wdth}:wordcloud'.format(typ=opustype, name=opusname, hght=height, wdth=width)
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
        progressid: str，作为被导入的 progress id
    """
    progressid = request.GET.get('progressid')
    if not progressid:
        return util.ctrl.infoMsg(_("{} 参数不能为空").format("Progress ID"))
    user = util.user.getCurrentUser(request)
    progress = Progress.objects.get_or_404(id=int(progressid))  # 获得作品.
    if progress.userid == user.id:  # 判断是否是自己的进度.
        return util.ctrl.infoMsg(_("您已拥有该进度，请不要重复添加"), title=_('导入失败'))
    # 生成 url
    url = '/progress/new'
    param = {
        'name': progress.name,
        'total': progress.total,
        'weblink': progress.weblink,
    }
    param_encoded = urllib.parse.urlencode(param)
    url_final = url + '?' + param_encoded  # ?name=xxx&total=xxx&weblink=xxx
    messages.success(request, _("已从 @{u} 导入进度《{n}》的信息").format(u=user.nickname, n=progress.name))
    messages.warning(request, _("请确认后点击“保存”"))
    return redirect(url_final)
