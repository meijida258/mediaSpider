from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

# Create your models here.

class User(models.Model):
    # 观众登录名
    username = models.TextField(max_length=30, unique=True)
    # 登录密码
    password = models.TextField(max_length=10)


class Room(models.Model):
    # 房间名
    name = models.TextField(max_length=50, unique=True)
    # url的增加字段
    slug = models.SlugField()
    # 创建者
    owner = models.ForeignKey(User)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Room, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chatroom:room-detail', kwargs={"slug": self.slug})


class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages")
    user = models.ForeignKey(User)

    content = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Message)
