import os
import datetime

from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.cache import cache
import KyanToolKit

import util.ctrl
ktk = KyanToolKit.KyanToolKit()


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

    def __str__(self):  # 用于需要 string 时的处理 python3
        return "{self.id}) {created} - @{self.nickname} : {self.username}".format(self=self, created=util.ctrl.formatDate(self.created))

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
            return UserExp.objects.get_or_create(userid=self.id, category=category).first()
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
        if mode == 'sent':
            return Chat.objects.filter(senderid=self.id).order_by('-created')
        if mode == 'unread':
            return Chat.objects.filter(receiverid=self.id, isread=False)


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

    # Category
    def setCategory(self, category):
        self.category = category

    # Exp
    def setExp(self, exp):
        self.exp = exp

    def addExp(self, exp, operation):
        self.setExp(self.exp + exp)
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

    def __str__(self):
        userexp = self.getUserexp()
        user = userexp.user
        return "{self.id}) {created} - @{user.nickname}: [{category_name}] {self.operation} +{self.change}".format(self=self, user=user, created=util.ctrl.formatDate(self.created), category_name=userexp.category_zh)

    def getUserexp(self):
        return UserExp.objects.get(id=self.userexpid)


class Opus(BaseModel):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)

    def __str__(self):
        subtext = "({self.subtitle})".format(self=self) if self.subtitle else ""
        total = self.total if self.total else '∞'
        return "{self.id}) 《 {self.name} 》 {subtext} [{total}]".format(self=self, subtext=subtext, total=total)

    def getProgress(self):
        return Progress.objects.get(opusid=self.id)

    def getCoverColor(self):
        cache_key = 'opus:{}:covercolor'.format(self.id)
        cached_color = cache.get(cache_key)
        return cached_color or cache_key


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
            result['average_created_modified'] = util.ctrl.formatTimedelta(temp_c2m_total / count, '%d %H %M') if count else 0
            result['average_created_now'] = util.ctrl.formatTimedelta(temp_c2n_total / count, '%d %H %M') if count else 0
            result['average_modified_now'] = util.ctrl.formatTimedelta(temp_m2n_total / count, '%d %H %M') if count else 0
        return result


class Progress(BaseModel):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
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
        'done': '已完成',
        'error': '出错',
        'todo': '待阅读',
        'follow': '追剧中',
    }
    objects = ProgressManager()

    def __str__(self):
        return "{self.id}) @{self.user.nickname} -《 {self.opus.name} 》 ({self.current}/{opus.total})".format(self=self)

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

    # status
    def setStatus(self, status):
        if status not in self.status_pool.get('all'):
            raise Exception("状态只能为 {pool}".format(pool=str(self.status_pool.get('all'))))
        self.status = status

    def setStatusAuto(self):
        opus = self.opus
        if self.status == 'giveup':
            return True
        if self.current == 0:
            self.setStatus('todo')
            return True
        if opus.total == 0:
            self.setStatus('follow')
            return True
        if self.current > opus.total:
            self.setStatus('error')
            return True
        if self.current == opus.total:
            self.setStatus('done')
            return True
        if self.current < opus.total:
            self.setStatus('inprogress')
            return True
        return False

    def resetStatus(self):
        self.setStatus('error')
        return self.setStatusAuto()

    def getStatus(self):
        status_name = self.status_name.get(self.status)
        if status_name:
            return status_name
        return self.status

    # calculations
    @property
    def persent(self):
        opus = self.opus
        if opus.total == 0:
            total = int(self.current) + 1
        else:
            total = int(opus.total)
        persent = int(self.current) / total * 100
        return int(persent)

    def getBartype(self):
        persent = self.persent
        if persent < 33:
            bartype = 'progress-bar-danger'
        elif persent < 66:
            bartype = 'progress-bar-warning'
        elif persent < 100:
            bartype = 'progress-bar-success'
        else:
            bartype = 'progress-bar-primary'
        return bartype

    @property
    def opus(self):
        return Opus.objects.get(id=self.opusid)

    @property
    def user(self):
        return User.objects.get(id=self.userid)


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
                'email': 'syschat@superfarmer.net',
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

    def __str__(self):
        sender = self.getSender()
        receiver = self.getReceiver()
        unread = "" if self.isread else "[unread]"
        content = (self.content[:40] + '..') if len(self.content) > 40 else self.content
        return "{self.id}) {created} - @{sender.nickname}→@{receiver.nickname} : {unread} {content}".format(self=self, created=util.ctrl.formatDate(self.created), sender=sender, receiver=receiver, content=content, unread=unread)

    # send / receive / isread
    def markRead(self):
        self.isread = True
        self.save()
        return True

    def markUnread(self):
        self.isread = False
        self.save()
        return True

    # util
    def getSender(self):
        return User.objects.get(id=self.senderid)

    def getReceiver(self):
        return User.objects.get(id=self.receiverid)
