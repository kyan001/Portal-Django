from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from util.ctrl import *
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
        self.created = str(self.created)
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()

class Opus(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(default=0)
    created = models.DateTimeField()
    objects = OpusManager();
    def __str__(self):
        subtext = "(" + self.subtitle + ")" if self.subtitle else "";
        return str(self.id) + ': <<{0}>>{1}[{2}]'.format(self.name, subtext, str(self.total))
    def toArray(self):
        self.created = str(self.created)
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()

class OpusManager(models.Manager):
    def findfirst(self, opusid):
        if not opusid:
            raise Exception("请输入作品 ID")
        try:
            opus = self.get(id=opusid)
        except Opus.DoesNotExist:
            return infoMsg("未找到 id 为 {0} 的作品".format(str(opusid)))
        return opus

class Progress(models.Model):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    def __str__(self):
        return str(self.id) + ": usr{0}.ops{1}".format(str(self.userid), str(self.opusid))
    def toArray(self):
        self.created = str(self.created)
        self.modified = str(self.modified)
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
        self.modified = timezone.now()
    def setModified(self):
        self.modified = timezone.now()
    def setStatus(self, status):
        status_pool = ('done','giveup','inprogress','error')
        if status not in status_pool:
            raise Exception("状态只能为 {0}".format(str(status_pool)))
        self.status = status

