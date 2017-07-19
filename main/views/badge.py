from django.shortcuts import render
from main.models import UserPermissionBadge
import util.ctrl

import KyanToolKit
ktk = KyanToolKit.KyanToolKit()


def list(request):
    '''获得所有徽章列表'''
    context = {}
    upbs = UserPermissionBadge.objects.all()
    context['upbs'] = upbs
    return render(request, 'badge/list.html', context)


def detail(request):
    '''查看单个徽章'''
    context = {}
    # 获得参数
    badgeid = request.GET.get('id')
    if not badgeid:
        return util.ctrl.infoMsg("需要一个徽章 id")
    # 获得作品
    badge = UserPermissionBadge.objects.get_or_404(id=badgeid)
    # render
    context['badge'] = badge
    return render(request, 'badge/detail.html', context)
