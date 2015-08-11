from django.db import models
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
        return self.nickname + "(" + self.username + ")"
    def getGravatar(self):
        base_src = "https://secure.gravatar.com/avatar/"
        email_md5 = ktk.md5(self.email) if self.email else "";
        return base_src + email_md5
