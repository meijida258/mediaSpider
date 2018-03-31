from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())

class RoomForm(forms.Form):
    name = forms.CharField(label='房间名',max_length=100)
    slug = forms.CharField(label='url后缀',max_length=100)
    owner = forms.CharField(label='房主名',max_length=100)