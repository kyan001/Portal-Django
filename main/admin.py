from django.contrib import admin

# Register your models here.
from .models import User, Opus, Progress

admin.site.register(User)
admin.site.register(Opus)
admin.site.register(Progress)
