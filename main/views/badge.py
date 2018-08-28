from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _

from main.models import UserPermissionBadge
import util.ctrl


def list(request):
    '''获得所有徽章列表'''
    context = {}
    upbs = UserPermissionBadge.objects.all()
    context['upbs'] = upbs
    return render(request, 'badge/list.html', context)


def detail(request):
    '''查看单个徽章'''
    context = {}
    # get inputs
    badgeid = request.GET.get('id')
    if not badgeid:
        raise Http404(_("{} 参数不能为空").format("Badge ID"))
    # get badge
    badge = UserPermissionBadge.objects.get_or_404(id=badgeid)
    # render
    context['badge'] = badge
    return render(request, 'badge/detail.html', context)
