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
    created = models.DateTimeField()
    def __str__(self): # 用于需要 string 时的处理 python3
        return str(self.id) + ":" + self.nickname + "(" + self.username + ")"
    def toArray(self):
        self.created = self.created.isoformat(' ')
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)

class Opus(models.Model):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)
    created = models.DateTimeField()
    def __str__(self):
        subtext = "(" + self.subtitle + ")" if self.subtitle else "";
        total = self.total if self.total else '∞'
        return str(self.id) + ': <<{0}>>{1}[{2}]'.format(self.name, subtext, str(total))
    def toArray(self):
        self.created = self.created.isoformat(' ')
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        return util.ctrl.formatDate(self.created)
    def getProgress(self):
        return Progress.objects.get(opusid=self.id)

class Progress(models.Model):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    weblink = models.URLField(max_length=2083, blank=True, default="")
    created = models.DateTimeField()
    modified = models.DateTimeField()
    status_pool = {
        'all' : ('inprogress','follow','todo','done','giveup','error'),
        'active' : ('inprogress','follow','todo','error'),
        'archive' : ('done','giveup'),
    }
    def __str__(self):
        opus = self.getOpus()
        user = self.getUser()
        return str(self.id) + ": {0}({1}) - 《{2}》({3}/{4})".format(user.username, user.nickname, opus.name, str(self.current), str(opus.total))
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
        if self.status == 'giveup':
            return '弃置';
        if self.status == 'error':
            return '出错';
        if self.status == 'done':
            return '已完成';
        if self.status == 'inprogress':
            return '进行中';
        if self.status == 'follow':
            return '追剧中';
        if self.status == 'todo':
            return '待阅读';
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

