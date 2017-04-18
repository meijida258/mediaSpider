from django.shortcuts import render
from django.http import HttpResponse
from .localfiles import porn

def index(request):
    return HttpResponse(u'1')
# Create your views here.

def add(request):
    a = request.GET.get('a', 0)
    b = request.GET.get('b', 0)
    c = a + b
    return HttpResponse(str(c))

def home(request):
    return render(request, 'home.html')

def porn_(request):
    page = request.GET.get('page', 1)
    num = request.GET.get('num', 1)
    type = request.GET.get('type')
    string = porn.porn.get(str(type),int(page), int(num))
    return render(request, 'porn.html', {'string': string})