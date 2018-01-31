import collections

from django.shortcuts import render
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import Http404
from django.utils.translation import gettext as _

from main.models import Chat, User
import util.ctrl
import util.user
import util.userexp


@util.user.login_required
def inbox(request):
    """用户查看自己的 inbox"""
    context = {}
    # get inputs
    filter_type = request.GET.get('type') or 'received'
    # get chats
    user = util.user.getCurrentUser(request)
    MSG_FILTERS = collections.OrderedDict()
    MSG_FILTERS['received'] = _('所有')
    MSG_FILTERS['unread'] = _('未读')
    MSG_FILTERS['quicknote'] = _('临时笔记')
    MSG_FILTERS['fromsys'] = _('系统')
    MSG_FILTERS['fromhuman'] = _('好友')
    MSG_FILTERS['sent'] = _('已发送')
    chat_list = user.getChats(filter_type) if filter_type in MSG_FILTERS.keys() else user.getChats('received')
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
    # users in sender or receiver but not both
    chaters = {chat.sender for chat in chat_list} | {chat.receiver for chat in chat_list}
    chaters -= {user}
    chater_and_counts = [(ctr, chat_list.filter(
        Q(senderid=ctr.id) | Q(receiverid=ctr.id)
    ).count()) for ctr in chaters]
    # add exp
    util.userexp.addExp(user, 'chat', 1, _('查看收信箱'))
    # render
    context['chats'] = chats
    context['chater_and_counts'] = chater_and_counts
    context['msg_filters'] = {
        'this': filter_type,
        'thiszh': MSG_FILTERS.get(filter_type),
        'all': MSG_FILTERS,
    }
    return render(request, 'chat/inbox.html', context)


@util.user.login_required
def delete(request):
    """在 inbox 界面删除某条消息"""
    # get history.back
    if 'HTTP_REFERER' in request.META:
        href_back = request.META.get('HTTP_REFERER')
        response = redirect(href_back)
    else:
        response = redirect('/chat/inbox')
    # get inputs
    chat_id = request.GET.get('id')
    if not chat_id:
        raise Http404(_("{} 参数不能为空").format("Chat ID"))
    # get chat
    user = util.user.getCurrentUser(request)
    chat = Chat.objects.get_or_404(id=chat_id)
    if user.id != chat.receiverid and (not user.getUserpermission('superuser')):
        return util.ctrl.infoMsg(_("只有消息的接收者可以{}消息").format(_("删除")), title=_("删除失败"))
    chat.delete()
    # add exp
    util.userexp.addExp(user, 'chat', 1, _('删除了一条来自 @{} 的消息').format(chat.sender.nickname))
    # render
    return response


@util.user.login_required
def conversation(request):
    """进入一对一聊天页面"""
    context = {}
    # get inputs
    mode = request.GET.get('mode')
    user = util.user.getCurrentUser(request)
    if mode == 'quicknote':
        return redirect('/chat/conversation?receiver={user.nickname}'.format(user=user))
    title = request.GET.get('title')
    receiver_nickname = request.GET.get('receiver')
    if receiver_nickname:
        # get receiver
        receiver = User.objects.get_or_404(nickname=receiver_nickname)
        # get history
        condition1 = Q(receiverid=receiver.id) & Q(senderid=user.id)
        condition2 = Q(senderid=receiver.id) & Q(receiverid=user.id)
        chats = Chat.objects.filter(condition1 | condition2).order_by('-created')  # [0:10]
        context['chats'] = chats
        context['receiver'] = receiver
        # add exp
        util.userexp.addExp(user, 'chat', 1, _("查看与 @{} 的对话").format(receiver.nickname))
    # render
    context['title'] = title
    return render(request, 'chat/conversation.html', context)


@util.user.login_required
def send(request):
    """点击对话界面中的发送按钮后"""
    # get inputs
    title = request.POST.get('title')
    content = request.POST.get('content')
    if not content:
        raise Http404(_("{} 参数不能为空").format("Content"))
    receiver_nickname = request.POST.get('receiver')
    if not receiver_nickname:
        raise Http404(_("{} 参数不能为空").format("Receiver Nickname"))
    # get receiver
    receiver = User.objects.get_or_404(nickname=receiver_nickname)
    # send chat
    user = util.user.getCurrentUser(request)
    user.sendChat(receiver, title=title, content=content)
    # add exp
    util.userexp.addExp(user, 'chat', 2, _("向 @{} 发送消息").format(receiver.nickname))
    # render
    return redirect('/chat/conversation?receiver={receiver.nickname}'.format(receiver=receiver))


@util.user.login_required
def markread(request):  # AJAX
    """用户标记自己的 chat 消息为已读"""
    # get chat
    chatid = request.GET.get('chatid')
    user = util.user.getCurrentUser(request)
    chat = Chat.objects.get_or_none(id=chatid)
    if not chat:
        return util.ctrl.returnJsonError(_("您查找的消息 id: {} 并不存在").format(chatid))
    if chat.receiverid != user.id and (not user.getUserpermission('superuser')):
        return util.ctrl.returnJsonError(_("只有消息的接收者可以{}消息").format(_("更新")))
    # add exp
    util.userexp.addExp(user, 'chat', 2, _("阅读来自 @{} 的消息").format(chat.sender.nickname))
    # markread
    isSuccessed = chat.markRead()
    return util.ctrl.returnJsonResult(isSuccessed)
