from django.shortcuts import render
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
