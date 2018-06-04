import os
import datetime
import re
from collections import Counter

from django.http import Http404
from django.db import models
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

import util.ctrl
import util.time


class BaseManager(models.Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise Http404(_('您查找的 {t} 并不存在。（查询参数 {a} {k}）').format(t=self.model.__name__, a=args or '', k=kwargs or ''))


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = BaseManager()

    class Meta:
        abstract = True

    def toArray(self):
        self.created = self.created.isoformat(' ')
        self.modified = self.modified.isoformat(' ')
        return model_to_dict(self)


class User(BaseModel):
    def headimg_upload_to(self, filename):
        """return the path for headimg(ImageField) use

        New filename:
            <MEDIA_ROOT>/user/headimg/<filename>
        """
        newname = os.path.join('user', 'headimg', filename)
        return newname
    LOGIN_SESSION_KEY = 'logged:user:id'
    username = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255, unique=True)
    question = models.TextField()
    answer1 = models.CharField(max_length=128)
    answer2 = models.CharField(max_length=128, blank=True, null=True)
    tip = models.TextField(blank=True, null=True)
    email = models.EmailField()
    headimg = models.ImageField(default='', upload_to=headimg_upload_to, blank=True)

    def __str__(self):
        return "@{self.nickname}({self.username})".format(self=self)

    @property
    def headimg_url(self):
        if self.headimg and hasattr(self.headimg, 'url'):
            return self.headimg.url
        return ''

    @property
    def privatekey(self):
        return util.ctrl.salty(self.created)

    @property
    def level(self):
        userexps = self.getUserExp()
        total_exp = sum(ue.exp for ue in userexps)
        return util.ctrl.calcLevel(total_exp)

    @property
    def badges(self):
        user_permissions = UserPermission.objects.filter(userid=self.id)
        if user_permissions.exists():
            return [up.badge for up in user_permissions]
        return None

    # permission related
    def getUserpermission(self, category):
        up = UserPermission.objects.get_or_none(userid=self.id, category=category)
        return up.isallowed if up else None

    def setUserpermission(self, category, isallowed):
        up, iscreated = UserPermission.objects.update_or_create(
            userid=self.id,
            category=category,
            defaults={
                'isallowed': isallowed
            }
        )

    # exps related
    def getUserExp(self, category=None):
        if category:
            userexp, iscreated = UserExp.objects.get_or_create(userid=self.id, category=category)
            return userexp
        else:
            return UserExp.objects.filter(userid=self.id)

    # progress related
    def getProgressStatics(self):
        """Get uses's progress statics for all status"""
        result = {}
        for st, stzh in (Progress.STATUSES.get('active') + Progress.STATUSES.get('archive')):
            result[st] = Progress.objects.getStatusStatics(userid=self.id, status=st)
            result[st]['name'] = Progress.objects.getStatusName(st)
        return result

    # chat related
    def sendChat(self, receiver, title="", content=""):
        new_chat = Chat(senderid=self.id, receiverid=receiver.id, title=title, content=content.strip())
        new_chat.save()
        return new_chat

    def getChats(self, mode=None):
        if mode == 'received':
            chats = Chat.objects.filter(receiverid=self.id)
        elif mode == 'sent':
            chats = Chat.objects.filter(senderid=self.id).exclude(receiverid=self.id)
        elif mode == 'unread':
            chats = Chat.objects.filter(receiverid=self.id, isread=False)
        elif mode == 'fromsys':
            syschatuser = Chat.objects.getSyschatUser()
            chats = Chat.objects.filter(senderid=syschatuser.id, receiverid=self.id)
        elif mode == 'fromhuman':
            syschatuser = Chat.objects.getSyschatUser()
            chats = Chat.objects.filter(receiverid=self.id).exclude(senderid=syschatuser.id).exclude(senderid=self.id)
        elif mode == 'quicknote':
            chats = Chat.objects.filter(receiverid=self.id, senderid=self.id)
        else:
            chats = Chat.objects.filter(receiverid=self.id)
        return chats.order_by('-created')


class UserPermission(BaseModel):
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=128, blank=False, null=False)
    isallowed = models.BooleanField()

    @property
    def user(self):
        return User.objects.get_or_404(id=self.userid)

    @property
    def badge(self):
        badge = UserPermissionBadge.objects.get_or_none(category=self.category, isallowed=self.isallowed)
        return badge or None

    def __str__(self):
        if User.objects.filter(id=self.userid).exists():
            return "@{self.user.nickname} - {self.category} : {self.isallowed}".format(self=self)
        else:
            return "USER_DELETED"


class UserPermissionBadge(BaseModel):
    category = models.CharField(max_length=128, blank=False, null=False)
    isallowed = models.BooleanField()
    image = models.TextField(default='/static/media/badges/no.png')
    description = models.TextField(default='')
    requirement = models.TextField(default='')
    designernname = models.CharField(default="", max_length=128, blank=True, null=True)

    @property
    def designer(self):  # may not have a designer user but only a designer nickname
        if not self.designernname:
            return None
        return User.objects.get_or_none(nickname=self.designernname)

    def __str__(self):
        return "{self.category}: {self.isallowed}".format(self=self)

    def userCount(self):
        return UserPermission.objects.filter(category=self.category, isallowed=self.isallowed).count()


class UserExp(BaseModel):
    CATEGORIES = (
        ('progress', _('进度活跃度')),
        ('user', _('用户活跃度')),
        ('chat', _('消息活跃度')),
        ('error', _('错误类别')),
    )
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=255, blank=False, null=False, choices=CATEGORIES)
    exp = models.IntegerField(default=0, blank=False, null=False)

    def __str__(self):
        if User.objects.filter(id=self.userid).exists():
            return "@{self.user.nickname} - {category_name}".format(self=self, category_name=self.get_category_display())
        else:
            return "USER_DELETED"

    @property
    def level(self):
        return util.ctrl.calcLevel(self.exp)

    @property
    def user(self):
        return User.objects.get_or_404(id=self.userid)

    @property
    def persent(self):
        level = self.level
        prev_exp = util.ctrl.calcExp(level)
        next_exp = util.ctrl.calcExp(level + 1)
        exp_need = next_exp - prev_exp
        exp_have = self.exp - prev_exp
        persent = exp_have / exp_need * 100
        return int(persent)

    def add(self, incr, operation):
        with transaction.atomic():
            self.exp += incr
            self.save()
            history = ExpHistory(userexpid=self.id, operation=operation, change=incr)
            history.save()

    def getExpHistory(self, count=0):
        result = ExpHistory.objects.filter(userexpid=self.id).order_by('-created')
        if isinstance(count, int) and count > 0:
            return result[0:count]
        return result


class ExpHistory(BaseModel):
    userexpid = models.IntegerField(default=0, blank=False, null=False)
    operation = models.TextField()
    change = models.IntegerField(default=0, blank=False, null=False)

    @property
    def userexp(self):
        return UserExp.objects.get_or_404(id=self.userexpid)

    def __str__(self):
        if UserExp.objects.filter(id=self.userexpid).exists() and User.objects.filter(id=self.userexp.userid).exists():
            return "{self.id}) {created} - @{self.userexp.user.nickname}: [{category_name}] {self.operation} +{self.change}".format(self=self, created=util.time.formatDate(self.created), category_name=self.userexp.get_category_display())
        else:
            return "USER_DELETED"


class OpusManager(BaseManager):
    def getTopComments(self):
        """Count and return the top common comments

        Returns:
            sorted comment:count k-v dictionary
        """
        records = Opus.objects.all()
        sbttl_counts = {}
        for r in records:
            if not r.comment:
                continue
            count = sbttl_counts.get(r.comment, 0)
            sbttl_counts[r.comment] = count + 1
        return sorted(sbttl_counts.items(), key=lambda itm: itm[1], reverse=True)

    def getCommentTags(self, opuses):
        MAX_TAGS = 9
        SUGGEST_COMMENTS = [_("书"), "PDF", _("漫画"), _("动画"), _("电视剧"), _("公开课"), _("纪录片"), _("视频"), _("小说")]
        if not opuses:
            raise Http404(_("{} 参数不能为空").format("Opuses"))
        comments = [opus.comment for opus in opuses if opus.comment and opus.comment.strip()]
        valid_tags = [tag for comment in comments for tag in re.split('[\s,，]+', comment) if len(tag.encode('gbk')) <= 10]
        comment_tags = [tag for tag, count in Counter(valid_tags).most_common(MAX_TAGS) if count > 2]
        if len(comment_tags) < MAX_TAGS:
            comment_tags.extend([sc for sc in SUGGEST_COMMENTS if sc not in comment_tags])
            comment_tags = comment_tags[:MAX_TAGS]
        return comment_tags


class Opus(BaseModel):
    name = models.CharField(max_length=255)
    comment = models.TextField(blank=True, default='')
    total = models.IntegerField(default=0)
    objects = OpusManager()

    @property
    def progress(self):
        return Progress.objects.get_or_404(opusid=self.id)

    @property
    def covercolor(self):
        cache_key = 'opus:{}:covercolor'.format(self.id)
        cached_color = cache.get(cache_key)
        return cached_color or None

    def __str__(self):
        subtext = "({self.comment})".format(self=self) if self.comment else ""
        total = self.total if self.total else '∞'
        return "《{self.name}》{subtext}[{total}]".format(self=self, subtext=subtext, total=total)


class ProgressManager(BaseManager):
    def getStatusName(self, status):
        """Get a status' Chinese translation"""
        status_names = dict(Progress.STATUSES.get('active') + Progress.STATUSES.get('archive'))
        status_name = status_names.get(status)
        return status_name or status

    def getStatusStatics(self, status, userid):
        """Get the statics for one status"""
        result = {}
        if status in dict(Progress.STATUSES.get('active') + Progress.STATUSES.get('archive')).keys():
            records = Progress.objects.filter(userid=userid, status=status)
            # count
            count = records.count()
            result['count'] = count
            # average time spent
            temp_c2m_total = temp_c2n_total = temp_m2n_total = datetime.timedelta()
            for r in records:
                temp_c2m_total += r.getTimedelta('c2m')
                temp_c2n_total += r.getTimedelta('c2n')
                temp_m2n_total += r.getTimedelta('m2n')
            result['average_created_modified'] = util.time.formatTimedelta(temp_c2m_total / count, '%d %H %M') if count else 0
            result['average_created_now'] = util.time.formatTimedelta(temp_c2n_total / count, '%d %H %M') if count else 0
            result['average_modified_now'] = util.time.formatTimedelta(temp_m2n_total / count, '%d %H %M') if count else 0
        return result


class Progress(BaseModel):
    STATUSES = {
        'active': (
            ('inprogress', _('进行中')),
            ('follow', _('追剧中')),
            ('todo', _('待阅读')),
            ('error', _('出错')),
        ),
        'archive': (
            ('done', _('已完成')),
            ('deactivated', _('冻结中')),
        ),
    }
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUSES.items())
    weblink = models.URLField(max_length=2083, blank=True, default="")
    objects = ProgressManager()

    def save(self, *args, **kwargs):
        if self._setStatusAuto():
            super().save(*args, **kwargs)
        else:
            raise Http404(_("更新进度状态失败"))

    @property
    def persent(self):
        opus = self.opus
        if opus.total == 0:
            total = int(self.current) + 1
        else:
            total = int(opus.total)
        persent = int(self.current) / total * 100
        return int(persent)

    @property
    def opus(self):
        return Opus.objects.get_or_404(id=self.opusid)

    @property
    def user(self):
        return User.objects.get_or_404(id=self.userid)

    @property
    def link(self):
        return "<a href='/progress/detail?id={id}'>{name}</a>".format(id=self.id, name=self.opus.name)

    @property
    def contextual(self):
        persent = self.persent
        if self.current == 0:  # todo
            contextual_type = None
        elif persent < 30:
            contextual_type = 'danger'
        elif persent < 60:
            contextual_type = 'warning'
        elif persent < 90:
            contextual_type = 'success'
        elif persent < 100:
            contextual_type = 'info'
        elif persent == 100:  # done
            contextual_type = 'primary'
        else:
            raise Http404(_("上下文类型错误"))  # Contextual Type Error
        return contextual_type

    def __str__(self):
        if User.objects.filter(id=self.userid).exists():
            return "《{self.opus.name}》({self.current}/{self.opus.total}) {self.status}".format(self=self)
        else:
            return "USER_DELETED"

    # time spent
    def getTimedelta(self, mode='default'):
        if mode == 'c2m':
            return self.modified - self.created
        elif mode == 'c2n':
            return timezone.now() - self.created
        elif mode == 'm2n':
            return timezone.now() - self.modified
        elif mode == 'speed':
            return (self.getTimedelta('c2m') / self.current) if self.current else None
        else:
            return datetime.timedelta()

    def _setStatusAuto(self):
        opus = self.opus
        if self.status == 'deactivated':
            return True
        if self.current == 0:
            self.status = 'todo'
            return True
        if opus.total == 0:
            self.status = 'follow'
            return True
        if self.current > opus.total:
            self.status = 'error'
            return True
        if self.current == opus.total:
            self.status = 'done'
            return True
        if self.current < opus.total:
            self.status = 'inprogress'
            return True
        return False

    def resetStatus(self):
        self.status = 'error'
        return self._setStatusAuto()


class ChatManager(BaseManager):
    def sendBySys(self, receiver, title="", content=""):
        if not receiver:
            return False
        sysuser = self.getSyschatUser()
        return sysuser.sendChat(receiver, title, content)

    def getSyschatUser(self):
        sysuser, iscreated = User.objects.get_or_create(
            nickname='系统消息',
            defaults={
                'username': 'syschat',
                'question': 'syschat cannot be signined',
                'answer1': 'iknow',
                'email': 'syschat@kyan001.com',
            }
        )
        if iscreated:
            sysuser.setUserpermission('signin', False)
        return sysuser


class Chat(BaseModel):
    senderid = models.IntegerField(default=0, blank=False, null=False)
    receiverid = models.IntegerField(default=0, blank=False, null=False)
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    isread = models.BooleanField(default=False)
    objects = ChatManager()

    @property
    def sender(self):
        return User.objects.get_or_404(id=self.senderid)

    @property
    def receiver(self):
        return User.objects.get_or_404(id=self.receiverid)

    def __str__(self):
        if User.objects.filter(id=self.senderid).exists() and User.objects.filter(id=self.receiverid).exists():
            unread = "" if self.isread else "[unread]"
            content = (self.content[:40] + '..') if len(self.content) > 40 else self.content
            return "@{self.sender.nickname}→@{self.receiver.nickname} : {unread} {content}".format(self=self, created=util.time.formatDate(self.created), content=content, unread=unread)
        else:
            return "USER_DELETED"

    # send / receive / isread
    def markRead(self):
        self.isread = True
        self.save()
        return True

    def markUnread(self):
        self.isread = False
        self.save()
        return True
