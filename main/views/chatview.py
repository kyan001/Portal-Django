from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import *
from main.models import *
import util.ctrl

def chatInbox(request):
    '''用户查看自己的 inbox'''
    context = {}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get user
    try:
        user = User.objects.get(id=loginuser['id'])
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 id：{0} 并不存在".format(str(loginuser['id'])));
    # get inputs
    chat_type = request.GET.get('type')
    # get chats
    if chat_type == 'unread':
        chats = user.getUnreadChats()
    else:
        chats = user.getReceivedChats()
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(1, '查看收件箱')
    # render
    context['chats'] = chats
    context['user'] = user
    return render_to_response('chat/inbox.html', context)

def chatMarkread(request): # AJAX
    '''用户标记自己的 chat 消息为已读'''
    context = {}
    loginuser = request.session.get('loginuser')
    if not loginuser:
        return util.ctrl.returnJsonError("您还没有登入，请先登入")
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
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(1, '阅读消息')
    # markread
    isSuccessed = chat.markRead()
    return util.ctrl.returnJsonResult(True)
