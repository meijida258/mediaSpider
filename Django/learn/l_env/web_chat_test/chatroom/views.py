from django.shortcuts import render, render_to_response, Http404, HttpResponseRedirect
from django.db.utils import IntegrityError
from django.template import RequestContext
from .forms import UserForm
from .models import User

# Create your views here.

def index(request):
    return render_to_response('base.html')

def login(request):
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # 获取的表单数据与数据库进行比较
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                return HttpResponseRedirect('/chatroom/room_list.html')
            else:
                return render_to_response('accounts/login_failed.html', {'tip': '登录失败'})
    else:
        uf = UserForm()
    return render_to_response('accounts/login.html', {'uf': uf})

def sign_up(request):
    if request.method == "POST":
        uf = UserForm(request.POST)
        if uf.is_valid():
            # 获取表单信息
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # 将表单写入数据库
            user = User()
            user.username = username
            user.password = password
            try:
                user.save()
            except IntegrityError:
                return render_to_response('accounts/sign_up.html', {'uf': uf})
            # 返回注册成功页面
            return render_to_response('accounts/login.html')
    else:
        uf = UserForm()
    return render_to_response('accounts/sign_up.html', {'uf': uf})

def room_list(request):
    return render_to_response('chatroom/room_list.html')

# def create_room(request):
#     if request.method == "POST":
