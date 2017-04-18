from django.shortcuts import render,HttpResponse
import queue,json,time,hashlib
from django.core.cache import cache
from chat.templatetags import chatcus
from chat import models
import os
GLOBAL_MSG_QUEUES ={

}

# Create your views here.

def index(request):
    obj = models.UserProfile.objects.all()
    for i in obj:
        print (i.name)
    return render(request,'index.html')

def text(request):
    return render(request,'text.html')

#接受消息函数
def send_msg(request):
    #if request.POST.get()
    # 接受关于data的数据
    msg_data = request.POST.get('data')
    #判断是否正确
    if msg_data:
        msg_data = json.loads(msg_data)
        msg_data['timestamp'] = time.time()
        if msg_data['type'] == 'single':
            if not GLOBAL_MSG_QUEUES.get(int(msg_data['to']) ):
                GLOBAL_MSG_QUEUES[int(msg_data["to"])] = queue.Queue()
            GLOBAL_MSG_QUEUES[int(msg_data["to"])].put(msg_data)
        else:#group
            group_obj = models.ChatGroup.objects.get(id=msg_data['to'])
            for member in group_obj.members.select_related():
                if not GLOBAL_MSG_QUEUES.get(member.id): #如果字典里不存在这个用户的queue
                    GLOBAL_MSG_QUEUES[member.id] = queue.Queue()
                if member.id != request.user.userprofile.id:
                    GLOBAL_MSG_QUEUES[member.id].put(msg_data)
    return HttpResponse('---发送后端成功---')
def get_new_msgs(request):
    if request.user.userprofile.id not in GLOBAL_MSG_QUEUES:
        print("不存在[%s]" %request.user.userprofile.id,request.user)
        GLOBAL_MSG_QUEUES[request.user.userprofile.id] = queue.Queue()
    msg_count = GLOBAL_MSG_QUEUES[request.user.userprofile.id].qsize()
    q_obj = GLOBAL_MSG_QUEUES[request.user.userprofile.id]
    msg_list = []
    print(msg_list)
    if msg_count >0:
        for msg in range(msg_count):
            msg_list.append(q_obj.get())
        print("new msgs:",msg_list)
    else:#没消息,要挂起
        print("no new msg for ",request.user,request.user.userprofile.id)
        #print(GLOBAL_MSG_QUEUES)
        try:
            msg_list.append(q_obj.get(timeout=60))
        except queue.Empty:
            print("\033[41;1mno msg for [%s][%s] ,timeout\033[0m" %(request.user.userprofile.id,request.user))
    return HttpResponse(json.dumps(msg_list))

# 上传文件函数
def file_upload(request):
    print(request.POST,request.FILES)
    file_obj = request.FILES.get('file')
    user_home_dir = "uploads/%s" % request.user.userprofile.id
    if not os.path.isdir(user_home_dir):
        os.mkdir(user_home_dir)
    new_file_name= "%s/%s" %(user_home_dir,file_obj.name)
    recv_size = 0
    with open(new_file_name,"wb") as new_file_obj:
        for chunk in file_obj.chunks():
            new_file_obj.write(chunk)
            recv_size += len(chunk)
            cache.set(file_obj.name,recv_size)
    return HttpResponse("--upload success---")
def get_file_upload_progress(request):
    filename = request.GET.get("filename")
    progress = cache.get(filename)
    print("file[%s] uploading progress[%s]" %(filename,progress))
    return HttpResponse(json.dumps({"recv_size":progress}))
def file_upload_progress(request):
    if request.method == 'GET':
        print("----come....")
        filename = request.GET.get('filename')
        upload_progress = cache.get(filename)
        print('upload_progress:', upload_progress)

        return HttpResponse(json.dumps({"received_size":upload_progress}))
    else: #post ,clear cache key
        cache_key = request.POST.get('cache_key')
        cache.delete(cache_key)

        return HttpResponse("cache key[%s] got deleted" %cache_key)

def delete_cache_key(request):
    cache_key = request.GET.get("cache_key")
    cache.delete(cache_key)
    return HttpResponse("cache key [%s] got deleted" % cache_key)


# 查找好友

def search_firends(request):
    friend_name = request.POST.get('name')
    #判断是否正确
    if friend_name:
        friend_name = json.loads(friend_name)
        if models.UserProfile.objects.filter(name=friend_name):
            obj = models.UserProfile.objects.filter(name=friend_name)
            for i in obj:
                friends = {'img':chatcus.chat_url(i.head_img),'name':friend_name}
            return HttpResponse(json.dumps(friends))
        else:
            return HttpResponse('no')
