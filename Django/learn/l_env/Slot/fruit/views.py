from django.shortcuts import render, render_to_response, HttpResponse
from .slot_simulation import jp
from dwebsocket.decorators import require_websocket, accept_websocket
import json, time
# Create your views here.

def index(request):
    return render(request, 'slot.html')

@accept_websocket
def echo_once(request):
    if not request.is_websocket():#判断是不是websocket连接
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request,'slot.html')
    else:
        while True:
            data = jp.auto_play()
            request.websocket.send(json.dumps(data).encode())
            time.sleep(0.3)


