from django.db import models
from django.forms.models import model_to_dict
import util.ctrl
from django.utils import timezone
import json
import util.KyanToolKit_Py
ktk = util.KyanToolKit_Py.KyanToolKit_Py()

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255, unique=True)
    question = models.TextField()
    answer1 = models.CharField(max_length=128)
    answer2 = models.CharField(max_length=128, blank=True, null=True)
    tip = models.TextField(blank=True, null=True)
    email = models.EmailField()
    created = models.DateTimeField(default=timezone.now, blank=True)
    def __str__(self): # 用于需要 string 时的处理 python3
        return "{0}: {1} - @{2} - {3}".format(str(self.id), self.getCreated(), self.username, self.nickname)
    def toArray(self):
        self.created = self.created.isoformat(' ')
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
    # permission related
    def getUserpermission(self, category):
        try:
            up = UserPermission.objects.get(userid=self.id, category=category)
            return up.isallowed
        except UserPermission.DoesNotExist:
            return None;
    def setUserpermission(self, category, isallowed):
        up = UserPermission.objects.update_or_create(userid=self.id, category=category,
            defaults={
                'isallowed': isallowed
            }
        )
    # exps related
    def getUserExp(self, category=None):
        if category:
            return UserExp.objects.get_or_create(userid=self.id, category=category)[0]
        else:
            return UserExp.objects.filter(userid=self.id)
    def getLevel(self):
        userexps = self.getUserExp()
        total_exp = sum(ue.exp for ue in userexps)
        return util.ctrl.calcLevel(total_exp)
    # progress related
    def getProgressCounts(self):
        countResult = {}
        for st in Progress.status_pool.get('all'):
            countResult[st] = Progress.objects.filter(userid=self.id, status=st).count()
        return countResult
    # chat related
    def sendChat(self, receiver, title="", content=""):
        new_chat = Chat(senderid=self.id, receiverid=receiver.id, title=title, content=content);
        new_chat.setCreated()
        new_chat.save()
        return True
    def getReceivedChats(self):
        return Chat.objects.filter(receiverid=self.id).order_by('-created')
    def getSentChats(self):
        return Chat.objects.filter(senderid=self.id).order_by('-created')
    def getUnreadChats(self):
        return Chat.objects.filter(receiverid=self.id, isread=False)

class UserPermissionManager(models.Manager):
    def getCategoryName(self, category):
        category_name = UserPermission.category_name.get(category)
        if category_name:
            return category_name;
        return category

class UserPermission(models.Model):
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=128, blank=False, null=False)
    isallowed = models.BooleanField()
    objects = UserPermissionManager()
    category_pool = {
        'all': ('signin'),
    }
    category_name = {
        'signin': '登入',
    }
    def __str__(self):
        user = self.getUser()
        return "{0}: @{1} - {2}: {3}".format(str(self.id), user.nickname, self.getCategoryName(), self.isallowed)
    def getUser(self):
        return User.objects.get(id=self.userid)
    def getCategoryName(self):
        category_name = self.category_name.get(self.category)
        if category_name:
            return category_name;
        return self.category

class UserExp(models.Model):
    userid = models.IntegerField(default=0, blank=False, null=False)
    category = models.CharField(max_length=255, blank=False, null=False)
    exp = models.IntegerField(default=0, blank=False, null=False)
    modified = models.DateTimeField(default=timezone.now, blank=True)
    created = models.DateTimeField(default=timezone.now, blank=True)
    category_pool = {
        'all' : ('progress','user','chat','error'),
    }
    category_name = {
        'progress': '进度活跃度',
        'user': '用户活跃度',
        'chat': '消息活跃度',
        'error': '错误类别',
    }
    def __str__(self):
        user = self.getUser()
        return str(self.id) + ": @{0} - {1}: {2} - lv{3}".format(user.nickname, self.getCategory(), str(self.exp), str(self.getLevel()))
    # Category
    def setCategory(self, category):
        if category not in self.category_pool.get('all'):
            raise Exception("分类只能为 {0}".format( str(category_pool.get('all')) ))
        self.category = category
        self.setModified()
    def getCategory(self):
        category_name = self.category_name.get(self.category)
        if category_name:
            return category_name
        return self.category
    # Created & Modified
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
    def setModified(self):
        self.modified = timezone.now()
    def getModified(self):
        return util.ctrl.formatDate(self.modified)
    # Exp
    def setExp(self, exp):
        self.exp = exp
        self.setModified()
    def addExp(self, exp, operation):
        self.setExp(self.exp + exp)
        history = ExpHistory(userexpid=self.id, operation=operation, change=exp)
        self.save()
        history.save()
    # calculations
    def getLevel(self):
        return util.ctrl.calcLevel(self.exp)
    def getLevelupExp(self):
        level = self.getLevel()
        return util.ctrl.calcExp(level+1)
    def getPersent(self):
        level = self.getLevel()
        prev_exp = util.ctrl.calcExp(level)
        next_exp = self.getLevelupExp()
        exp_need = next_exp - prev_exp
        exp_have = self.exp - prev_exp
        persent = exp_have / exp_need * 100
        return int(persent)
    def getUser(self):
        return User.objects.get(id=self.userid)
    def getExpHistory(self, count=0):
        result = ExpHistory.objects.filter(userexpid=self.id).order_by('-created')
        if isinstance(count,int) and count>0:
            return result[0:count]
        return result

class ExpHistory(models.Model):
    userexpid = models.IntegerField(default=0, blank=False, null=False)
    operation = models.TextField()
    change = models.IntegerField(default=0, blank=False, null=False)
    created = models.DateTimeField(default=timezone.now, blank=True)
    def __str__(self):
        userexp = self.getUserexp()
        user = userexp.getUser()
        return str(self.id) + ": {0} - @{1}: [{2}] {3} +{4}".format(
            self.getCreated(), user.nickname, userexp.getCategory(), self.operation, str(self.change)
        )
    def getUserexp(self):
        return UserExp.objects.get(id=self.userexpid)
    # Created & Modified
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)

class Opus(models.Model):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now, blank=True)
    def __str__(self):
        subtext = "(" + self.subtitle + ")" if self.subtitle else "";
        total = self.total if self.total else '∞'
        return str(self.id) + ': {0} {1} [{2}]'.format(self.name, subtext, str(total))
    def toArray(self):
        self.created = self.created.isoformat(' ')
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
    def getProgress(self):
        return Progress.objects.get(opusid=self.id)

class ProgressManager(models.Manager):
    def getStatusName(self, status):
        status_name = Progress.status_name.get(status)
        if status_name:
            return status_name;
        return status

class Progress(models.Model):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    weblink = models.URLField(max_length=2083, blank=True, default="")
    created = models.DateTimeField(default=timezone.now, blank=True)
    modified = models.DateTimeField(default=timezone.now, blank=True)
    status_pool = {
        'all' : ('inprogress','follow','todo','done','giveup','error'),
        'active' : ('inprogress','follow','todo','error'),
        'archive' : ('done','giveup'),
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
        opus = self.getOpus()
        user = self.getUser()
        return str(self.id) + ": @{0} - {1} ({2}/{3})".format(user.nickname, opus.name, str(self.current), str(opus.total))
    def toArray(self):
        self.created = self.created.isoformat(' ')
        self.modified = self.modified.isoformat(' ')
        return model_to_dict(self)
    # created & modified
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
    def setModified(self):
        self.modified = timezone.now()
    def getModified(self):
        return util.ctrl.formatDate(self.modified)
    # status
    def setStatus(self, status):
        if status not in self.status_pool.get('all'):
            raise Exception("状态只能为 {0}".format( str(status_pool.get('all')) ))
        self.status = status
        self.setModified()
    def setStatusAuto(self):
        opus = self.getOpus()
        if self.status == 'giveup':
            return True;
        if self.current == 0:
            self.setStatus('todo')
            return True;
        if opus.total == 0:
            self.setStatus('follow')
            return True;
        if self.current > opus.total:
            self.setStatus('error')
            return True;
        if self.current == opus.total:
            self.setStatus('done')
            return True;
        if self.current < opus.total:
            self.setStatus('inprogress')
            return True;
        return False
    def resetStatus(self):
        self.setStatus('error')
        return self.setStatusAuto()
    def getStatus(self):
        status_name = self.status_name.get(self.status)
        if status_name:
            return status_name;
        return self.status
    # calculations
    def getPersent(self):
        opus = self.getOpus()
        if opus.total == 0:
            total = int(self.current)+1
        else:
            total = int(opus.total)
        persent = int(self.current)/total*100
        return int(persent)
    def getBartype(self):
        persent = self.getPersent()
        if persent < 33:
            bartype = 'progress-bar-danger'
        elif persent < 66:
            bartype = 'progress-bar-warning'
        elif persent < 100:
            bartype = 'progress-bar-success'
        else:
            bartype = 'progress-bar-primary'
        return bartype
    def getOpus(self):
        return Opus.objects.get(id=self.opusid)
    def getUser(self):
        return User.objects.get(id=self.userid)

class ChatManager(models.Manager):
    def sendBySys(self, receiver, title="", content=""):
        if not receiver:
            return False
        sysuser, iscreated = User.objects.get_or_create(nickname='系统消息',
            defaults={
                'username': 'syschat',
                'question': 'syschat cannot be signined',
                'answer1': 'iknow',
                'email': 'syschat@superfarmer.net',
            }
        )
        if iscreated:
            sysuser.setUserpermission('signin', False)
        return sysuser.sendChat(receiver, title, content)

class Chat(models.Model):
    senderid = models.IntegerField(default=0, blank=False, null=False)
    receiverid = models.IntegerField(default=0, blank=False, null=False)
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    isread = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, blank=False)
    objects = ChatManager();
    def __str__(self):
        sender = self.getSender()
        receiver = self.getReceiver()
        result = "{0}: @{1} -> @{2} |{3} |{4}".format(str(self.id), sender.nickname, receiver.nickname, self.getCreated(), self.content)
        if not self.isread:
            result += " [unread]"
        return result
    # send / receive / isread
    def markRead(self):
        self.isread = True;
        self.save()
        return True;
    def markUnread(self):
        self.isread = False;
        self.save()
        return True;
    # util
    def getSender(self):
        return User.objects.get(id=self.senderid)
    def getReceiver(self):
        return User.objects.get(id=self.receiverid)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
