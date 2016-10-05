from django.shortcuts import render
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.models import UserExp, Chat, User
from django.db.models import Q
import util.ctrl
import util.user


def chatInbox(request):
    '''用户查看自己的 inbox'''
    context = {'request': request}
    user = util.user.getCurrentUser(request)
    if not user:
        return util.ctrl.infoMsg("您还没有登入，请先登入", title='请先登入', url='/user/signin')
    # get inputs
    chat_type = request.GET.get('type')
    # get chats
    if chat_type == 'unread':
        chat_list = user.getChats('unread')
    else:
        chat_list = user.getChats('received')
    # paginator
    paginator = Paginator(chat_list, per_page=15)
    page = request.GET.get('page')
    try:
        chats = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        chats = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        chats = paginator.page(paginator.num_pages)
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(1, '查看收件箱')
    # render
    context['chats'] = chats
    return render(request, 'chat/inbox.html', context)


def chatDelete(request):
    '''在 inbox 界面删除某条消息'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get history.back
    if 'HTTP_REFERER' in request.META:
        href_back = request.META.get('HTTP_REFERER')
        response = redirect(href_back)
    else:
        response = redirect('/chat/inbox')
    # get inputs
    chat_id = request.GET.get('id')
    if not chat_id:
        return util.ctrl.infoMsg("您输入的网址不完整，缺少参数 id")
    # get chat
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return util.ctrl.infoMsg("您查找的消息 id：{id} 并不存在".format(id=str(chat_id)))
    if user.id != chat.receiverid and (not user.getUserpermission('superuser')):
        return util.ctrl.infoMsg("只有消息的接收者可以删除消息")
    chat.delete()
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(1, '删除了一条来自 @{sender.nickname} 的消息'.format(sender=chat.sender))
    # render
    return response


def chatConversation(request):
    '''进入一对一聊天页面'''
    context = {'request': request}
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get inputs
    mode = request.GET.get('mode')
    if mode == 'quicknote':
        return redirect('/chat/conversation?receiver={user.nickname}'.format(user=user))
    receiver_nickname = request.GET.get('receiver')
    if receiver_nickname:
        # get receiver
        try:
            receiver = User.objects.get(nickname=receiver_nickname)
        except User.DoesNotExist:
            return util.ctrl.infoMsg("您查找的用户 @{nickname} 并不存在".format(nickname=str(receiver_nickname)))
        # get history
        condition1 = Q(receiverid=receiver.id) & Q(senderid=user.id)
        condition2 = Q(senderid=receiver.id) & Q(receiverid=user.id)
        chats = Chat.objects.filter(condition1 | condition2).order_by('-created')  # [0:10]
        context['chats'] = chats
        context['receiver'] = receiver
    title = request.GET.get('title')
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    if receiver_nickname:
        userexp.addExp(1, '查看与 @{receiver.nickname} 的对话'.format(receiver=receiver))
    # render
    context['title'] = title
    return render(request, 'chat/conversation.html', context)


def chatSend(request):
    '''点击对话界面中的发送按钮后'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.user.loginToContinue(request)
    # get inputs
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not content:
        return util.ctrl.infoMsg("请填写发送的内容，缺少参数 content")
    receiver_nickname = request.POST.get('receiver')
    if not receiver_nickname:
        return util.ctrl.infoMsg("您输入的网址不完整，缺少参数 receiver_nickname")
    # get receiver
    try:
        receiver = User.objects.get(nickname=receiver_nickname)
    except User.DoesNotExist:
        return util.ctrl.infoMsg("您查找的用户 @{nickname} 并不存在".format(nickname=str(receiver_nickname)))
    # send chat
    user.sendChat(receiver, title=title, content=content)
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(2, '向 @{receiver.nickname} 发送消息'.format(receiver=receiver))
    # render
    return redirect('/chat/conversation?receiver={receiver.nickname}'.format(receiver=receiver))


def chatMarkread(request):  # AJAX
    '''用户标记自己的 chat 消息为已读'''
    user = util.user.getCurrentUser(request)
    if not user:
        return util.ctrl.returnJsonError("您还没有登入，请先登入")
    # get chat
    chatid = request.GET.get('chatid')
    try:
        chat = Chat.objects.get(id=chatid)
    except Chat.DoesNotExist:
        return util.ctrl.returnJsonError("您查找的消息 id: {id} 并不存在".format(id=str(chatid)))
    if chat.receiverid != user.id and (not user.getUserpermission('superuser')):
        return util.ctrl.returnJsonError('你没有权限修改 id: {chat.id} 的消息'.format(chat=chat))
    # add exps
    userexp, created = UserExp.objects.get_or_create(userid=user.id, category='chat')
    userexp.addExp(2, '阅读来自 @{sender.nickname} 的消息'.format(sender=chat.sender))
    # markread
    isSuccessed = chat.markRead()
    return util.ctrl.returnJsonResult(isSuccessed)
