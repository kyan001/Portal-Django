from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import *
from django.views.decorators.csrf import csrf_exempt
from main.models import Chat, User
from django.core.cache import cache
import util.ctrl

import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

def chatInbox(request):
    '''用户查看自己的 inbox'''
    context = {}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return infoMsg("您查找的用户 id：{0} 并不存在".format(str(loginuser['id'])));
    # get chats
    chats = user.getReceivedChats()
    # render
    context['chats'] = chats
    return render_to_response('chat/inbox.html', context)

def chatMarkread(request): # AJAX
    '''用户标记自己的 chat 消息为已读'''
    context = {}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return returnJsonError("您还没有登入，请先登入")
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return util.ctrl.returnJsonError("您查找的用户 id：{0} 并不存在".format(str(loginuser['id'])));
    # get chat
    chatid = request.GET.get('chatid');
    try:
        chat = Chat.objects.get(id=chatid)
    except Chat.DoesNotExist:
        return util.ctrl.returnJsonError("您查找的消息 id: {0} 并不存在".format(str(chatid)))
    if chat.receiverid != user.id:
        return util.ctrl.returnJsonError('你没有权限修改 id: {0} 的消息'.format(str(chat.id)))
    # markread
    isSuccessed = chat.markRead()
    return util.ctrl.returnJsonResult(True)
