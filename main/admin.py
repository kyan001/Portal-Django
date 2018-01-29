from django.contrib import admin

# Register your models here.
from .models import *


class BaseModelAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display_links = ['id']


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    list_display = ('id', 'username', 'nickname', 'question', 'tip', 'email', 'headimg', 'created', 'modified')
    list_display_links = ('id', 'username', 'nickname')
    search_fields = ('username', 'nickname', 'question', 'tip', 'email')


@admin.register(UserPermission)
class UserPermissionAdmin(BaseModelAdmin):
    list_display = ('user', 'id', 'userid', 'category', 'isallowed', 'created', 'modified')
    list_filter = ('category', 'isallowed')
    search_fields = ('userid',)


@admin.register(UserPermissionBadge)
class UserPermissionBadgeAdmin(BaseModelAdmin):
    list_display = ('id', 'category', 'isallowed', 'image', 'description', 'requirement', 'designernname')
    list_filter = ('category', 'isallowed', 'designernname')
    search_fields = ('description', 'requirement', 'designernname')


@admin.register(UserExp)
class UserExpAdmin(BaseModelAdmin):
    list_display = ('user', 'id', 'userid', 'category', 'exp', 'created', 'modified')
    list_filter = ('category',)
    search_fields = ('userid',)


@admin.register(ExpHistory)
class ExpHistoryAdmin(BaseModelAdmin):
    list_display = ('userexp', 'id', 'userexpid', 'operation', 'change', 'created', 'modified')
    list_filter = ('change',)
    search_fields = ('operation', 'userexpid')


@admin.register(Opus)
class OpusAdmin(BaseModelAdmin):
    list_display = ('id', 'name', 'comment', 'total', 'created', 'modified')
    search_fields = ('name', 'comment', 'total')


@admin.register(Progress)
class ProgressAdmin(BaseModelAdmin):
    list_display = ('opus', 'user', 'id', 'userid', 'opusid', 'current', 'status', 'modified')
    list_filter = ('status',)
    search_fields = ('userid', 'opusid', 'weblink')


@admin.register(Chat)
class ChatAdmin(BaseModelAdmin):
    list_display = ('sender', 'receiver', 'id', 'senderid', 'receiverid', 'title', 'isread', 'created')
    list_filter = ('isread',)
    search_fields = ('senderid', 'receiverid', 'title', 'content')
