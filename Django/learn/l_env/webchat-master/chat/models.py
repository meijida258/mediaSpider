from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    '''
    用户表
    '''
    user = models.OneToOneField(User)
    #名字
    name = models.CharField(max_length=32)
    #签名
    signature= models.CharField(max_length=255,blank=True,null=True)
    #头像
    head_img = models.ImageField(blank=True,null=True,upload_to="uploads")
    #朋友
    friends = models.ManyToManyField('self',related_name='my_friends',blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

class ChatGroup(models.Model):
    #群组名称
    name = models.CharField(max_length=64)
    #描述
    brief = models.CharField(max_length=255,blank=True,null=True)
    #群主
    owner = models.ForeignKey(UserProfile)
    #群头像
    group_img = models.ImageField(blank=True,null=True,upload_to="uploads")
    #群管理员
    admins = models.ManyToManyField(UserProfile,blank=True,related_name='group_admins')
    #群成员
    members = models.ManyToManyField(UserProfile,blank=True,related_name='group_members')
    #最大成员
    max_members = models.IntegerField(default=200)
    def __str__(self):
        return  self.name
    class Meta:
        verbose_name='群组'
        verbose_name_plural = '群组'
