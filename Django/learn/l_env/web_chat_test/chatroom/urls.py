from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from .views import *
# from web import views
# from web import urls as web_urls
# from web_chat import urls as chat_urls

urlpatterns = [
    url(r'^$', index, name='homepage'),
    url(r'^accounts/login/', login, name='login'),
    url(r'^accounts/login_failed/', login, name='login_failed'),
    url(r'^accounts/sign_up/', sign_up, name='sign_up'),
    url(r'^chatroom/room_list/', room_list, name='room_list')
]