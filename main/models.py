from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from util.ctrl import *
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
        time_format = '%m-%d %H:%M %p'
        if self.created.year != timezone.now().year:
            time_format = '%Y-' + time_format
        return self.created.astimezone(timezone.get_current_timezone()).strftime(time_format)

class Opus(models.Model):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)
    created = models.DateTimeField()
    def __str__(self):
        subtext = "(" + self.subtitle + ")" if self.subtitle else "";
        return str(self.id) + ': <<{0}>>{1}[{2}]'.format(self.name, subtext, str(self.total))
    def toArray(self):
        self.created = self.created.isoformat(' ')
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
    def getCreated(self):
        time_format = '%m-%d %H:%M %p'
        if self.created.year != timezone.now().year:
            time_format = '%Y-' + time_format
        return self.created.astimezone(timezone.get_current_timezone()).strftime(time_format)
    def getProgress(self):
        return Progress.objects.get(opusid=self.id)

class Progress(models.Model):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    created = models.DateTimeField()
    modified = models.DateTimeField()
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
        time_format = '%m-%d %H:%M %p'
        if self.created.year != timezone.now().year:
            time_format = '%Y-' + time_format
        return self.created.astimezone(timezone.get_current_timezone()).strftime(time_format)
    def setModified(self):
        self.modified = timezone.now()
    def getModified(self):
        time_format = '%m-%d %H:%M %p'
        if self.modified.year != timezone.now().year:
            time_format = '%Y-' + time_format
        return self.modified.astimezone(timezone.get_current_timezone()).strftime(time_format)

    # status
    def setStatus(self, status):
        status_pool = ('done','inprogress','giveup','error')
        if status not in status_pool:
            raise Exception("状态只能为 {0}".format(str(status_pool)))
        self.status = status
        self.setModified()
    def setStatusAuto(self):
        opus = self.getOpus()
        if self.status == 'giveup':
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
        return self.status

    # calculations
    def getPersent(self):
        opus = self.getOpus()
        persent = int(self.current)/int(opus.total)*100
        return int(persent)
    def getBartype(self):
        opus = self.getOpus()
        persent = int(self.current)/int(opus.total)*100
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

