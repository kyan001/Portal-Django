import os
import datetime

from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.cache import cache

import util.ctrl
import util.time


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return "{self.id}) {created} - @{self.nickname} : {self.username}".format(self=self, created=util.time.formatDate(self.created))

    # permission related
    def getUserpermission(self, category):
        try:
            up = UserPermission.objects.get(userid=self.id, category=category)
            return up.isallowed
        except UserPermission.DoesNotExist:
            return None

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
        result = {}
        for st in Progress.status_pool.get('all'):
            result[st] = Progress.objects.getProgressStatics(userid=self.id, status=st)
            result[st]['name'] = Progress.objects.getStatusName(st)
        return result

    # chat related
    def sendChat(self, receiver, title="", content=""):
        new_chat = Chat(senderid=self.id, receiverid=receiver.id, title=title, content=content.strip())
        new_chat.save()
        return new_chat

    def getChats(self, mode=None):
        if mode == 'received':
            return Chat.objects.filter(receiverid=self.id).order_by('-created')
        elif mode == 'sent':
            return Chat.objects.filter(senderid=self.id).order_by('-created')
        elif mode == 'unread':
            return Chat.objects.filter(receiverid=self.id, isread=False).order_by('-created')
        elif mode == 'fromsys':
            syschatuser = Chat.objects.getSyschatUser()
            return Chat.objects.filter(senderid=syschatuser.id, receiverid=self.id).order_by('-created')
        elif mode == 'fromhuman':
            syschatuser = Chat.objects.getSyschatUser()
            return Chat.objects.filter(receiverid=self.id).exclude(senderid=syschatuser.id).order_by('-created')
        else:
            return Chat.objects.filter(receiverid=self.id)


class UserPermission(BaseModel):
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=128, blank=False, null=False)
    isallowed = models.BooleanField()

    @property
    def user(self):
        return User.objects.get(id=self.userid)

    @property
    def badge(self):
        try:
            badge = UserPermissionBadge.objects.get(category=self.category, isallowed=self.isallowed)
            return badge
        except UserPermissionBadge.DoesNotExist:
            return None

    def __str__(self):
        return "{self.id}) @{self.user.nickname} - {self.category} : {self.isallowed}".format(self=self)


class UserPermissionBadge(BaseModel):
    category = models.CharField(max_length=128, blank=False, null=False)
    isallowed = models.BooleanField()
    image = models.TextField(default='/static/media/badges/no.png')
    description = models.TextField(default='')
    requirement = models.TextField(default='')
    designernname = models.CharField(default="", max_length=128, blank=True, null=True)

    @property
    def designer(self):
        if not self.designernname:
            return None
        try:
            user = User.objects.get(nickname=self.designernname)
            return user
        except User.DoesNotExist:
            return None

    def __str__(self):
        return "{self.id}) {self.category}:{self.isallowed} - ({self.image}) @{dnn}".format(self=self, dnn=self.designernname)

    def userCount(self):
        try:
            user_permissions = UserPermission.objects.filter(category=self.category, isallowed=self.isallowed)
            return user_permissions.count()
        except UserPermission.DoesNotExist:
            return 0


class UserExp(BaseModel):
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=255, blank=False, null=False)
    exp = models.IntegerField(default=0, blank=False, null=False)
    category_name = {
        'progress': '进度活跃度',
        'user': '用户活跃度',
        'chat': '消息活跃度',
        'error': '错误类别',
    }

    def __str__(self):
        return "{self.id}) @{self.user.nickname} - {self.category_zh}: {self.exp} - Lv.{self.level}".format(self=self)

    @property
    def category_zh(self):
        category_name = self.category_name.get(self.category)
        return category_name or self.category

    @property
    def level(self):
        return util.ctrl.calcLevel(self.exp)

    @property
    def user(self):
        return User.objects.get(id=self.userid)

    @property
    def persent(self):
        level = self.level
        prev_exp = util.ctrl.calcExp(level)
        next_exp = util.ctrl.calcExp(level + 1)
        exp_need = next_exp - prev_exp
        exp_have = self.exp - prev_exp
        persent = exp_have / exp_need * 100
        return int(persent)

    def addExp(self, exp, operation):
        self.exp += exp
        history = ExpHistory(userexpid=self.id, operation=operation, change=exp)
        self.save()
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
        return UserExp.objects.get(id=self.userexpid)

    def __str__(self):
        return "{self.id}) {created} - @{self.userexp.user.nickname}: [{self.userexp.category_zh}] {self.operation} +{self.change}".format(self=self, created=util.time.formatDate(self.created))


class OpusManager(models.Manager):
    def getTopSubtitles(self):
        """Count and return the top common subtitles

        Returns:
            sorted subtitle:count k-v dictionary
        """
        records = Opus.objects.all()
        sbttl_counts = {}
        for r in records:
            if not r.subtitle:
                continue
            count = sbttl_counts.get(r.subtitle, 0)
            sbttl_counts[r.subtitle] = count + 1
        return sorted(sbttl_counts.items(), key=lambda itm: itm[1], reverse=True)


class Opus(BaseModel):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)
    objects = OpusManager()

    @property
    def progress(self):
        return Progress.objects.get(opusid=self.id)

    @property
    def covercolor(self):
        cache_key = 'opus:{}:covercolor'.format(self.id)
        cached_color = cache.get(cache_key)
        return cached_color or None

    def __str__(self):
        subtext = "({self.subtitle})".format(self=self) if self.subtitle else ""
        total = self.total if self.total else '∞'
        return "{self.id}) 《 {self.name} 》 {subtext} [{total}]".format(self=self, subtext=subtext, total=total)


class ProgressManager(models.Manager):
    def getStatusName(self, status):
        status_name = Progress.status_name.get(status)
        if status_name:
            return status_name
        return status

    def getProgressStatics(self, status, userid):
        result = {}
        if status in Progress.status_pool.get('all'):
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
        'inprogress': '进行中',
        'follow': '追剧中',
        'todo': '待阅读',
        'done': '已完成',
        'giveup': '冻结中',
        'error': '出错',
    }
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=tuple(STATUSES.items()))
    weblink = models.URLField(max_length=2083, blank=True, default="")
    status_pool = {
        'all': ('inprogress', 'follow', 'todo', 'done', 'giveup', 'error'),
        'active': ('inprogress', 'follow', 'todo', 'error'),
        'archive': ('done', 'giveup'),
    }
    status_name = {
        'done': '已完成',
        'inprogress': '进行中',
        'giveup': '冻结中',
        'error': '出错',
        'todo': '待阅读',
        'follow': '追剧中',
    }
    objects = ProgressManager()

    @property
    def status_zh(self):
        status_name = self.status_name.get(self.status)
        return status_name or self.status

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
        return Opus.objects.get(id=self.opusid)

    @property
    def user(self):
        return User.objects.get(id=self.userid)

    @property
    def link(self):
        return "<a href='/progress/detail?id={id}'>{name}</a>".format(id=self.id, name=self.opus.name)

    def __str__(self):
        return "{self.id}) @{self.user.nickname} -《 {self.opus.name} 》 ({self.current}/{self.opus.total})".format(self=self)

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

    def setStatusAuto(self):
        opus = self.opus
        if self.status == 'giveup':
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
        return self.setStatusAuto()

    # calculations
    def getContextualType(self):
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
            raise Exception('Contextual Type Error')
        return contextual_type


class ChatManager(models.Manager):
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
        return User.objects.get(id=self.senderid)

    @property
    def receiver(self):
        return User.objects.get(id=self.receiverid)

    def __str__(self):
        unread = "" if self.isread else "[unread]"
        content = (self.content[:40] + '..') if len(self.content) > 40 else self.content
        return "{self.id}) {created} - @{self.sender.nickname}→@{self.receiver.nickname} : {unread} {content}".format(self=self, created=util.time.formatDate(self.created), content=content, unread=unread)

    # send / receive / isread
    def markRead(self):
        self.isread = True
        self.save()
        return True

    def markUnread(self):
        self.isread = False
        self.save()
        return True
