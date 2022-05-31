from django.contrib import admin
from . import models


@admin.register(models.InstaPK)
class InstaPKAdmin(admin.ModelAdmin) :
    list_display = ['insta_pk', 'status', 'page_target']
    ordering = ['status']


@admin.register(models.MyInstaPage)
class MyInstaPageAdmin(admin.ModelAdmin) :
    list_display = ['user_key', 'username', 'user_id']
    ordering = ['username']


@admin.register(models.CommentForUse)
class CommentForUseAdmin(admin.ModelAdmin):
    list_display = ['comment']
