from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import UserPermissionBadge
import util.ctrl

import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def badgeList(request):
    '''获得所有徽章列表'''
    context = {'request': request}
    upbs = UserPermissionBadge.objects.all()
    context['upbs'] = upbs
    return render_to_response('badge/list.html', context)

def badgeDetail(request):
    '''查看单个徽章'''
    context = {'request': request}
    #获得参数
    badgeid = request.GET.get('id')
    if not badgeid:
        return util.ctrl.infoMsg("需要一个徽章 id")
    #获得作品
    try:
        badge = UserPermissionBadge.objects.get(id=badgeid)
    except UserPermissionBadge.DoesNotExist:
        return util.ctrl.infoMsg("未找到 id 为 {id} 的徽章".format(id=str(badgeid)))
    # render
    context['badge'] = badge
    return render_to_response('badge/detail.html', context)
