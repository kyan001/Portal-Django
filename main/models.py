from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
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
    def __str__(self):
        if self.subtitle:
            return str(self.id) + ': <<{0}>>({1})[{2}]'.format(self.name, self.subtitle, str(self.total))
        else:
            return '<<{0}>>[{2}]'.format(self.name, str(self.total))
    def toArray(self):
        self.created = str(self.created)
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()

class Progress(models.Model):
    userid = models.IntegerField(default=0)
    opusid = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    status = models.CharField(max_length=50)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    def __str__(self):
        return str(self.id) + ": usr{0}.ops{1}".format(str(userid), str(opusid))
    def toArray(self):
        self.created = str(self.created)
        self.modified = str(self.modified)
        return model_to_dict(self)
    def setCreated(self):
        self.created = timezone.now()
        self.modified = timezone.now()
    def setModified(self):
        self.modified = timezone.now()
