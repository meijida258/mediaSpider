from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse
import time

def index(request):
    return render(request, 'index.html')
@accept_websocket
def echo(request):
    if not request.is_websocket():#判断是不是websocket连接
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request,'index.html')
    else:
        for message in request.websocket:
            while True:
                request.websocket.send(message)#发送消息到客户端
                time.sleep(2)
