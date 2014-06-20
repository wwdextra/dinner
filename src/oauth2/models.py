# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import force_unicode

class WeiboUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    weibo_user_id = models.BigIntegerField()
    weibo_username = models.CharField(max_length=20)
    create_datetime = models.DateTimeField(auto_now_add=True)
    oauth_access_token = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.user.username)
    class Admin:
        pass

#不推荐获取用户QQ号码，
class QQUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    qq_user_id = models.CharField(max_length=32) #openid
    qq_nickname = models.CharField(max_length=20)
    create_datetime = models.DateTimeField(auto_now_add=True)
    oauth_access_token = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username.encode('utf-8')
    def __unicode__(self):
        return force_unicode(self.user.username)
    class Admin:
        pass