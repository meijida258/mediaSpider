import itchat
import time, random
from itchat.content import *
import requests

isFriendChat = True
isGroupChat = False
isMpChat = True

toUserName = ''

def get_response(req):
    response = requests.get('http://220.166.65.195/chatbot/say?content={}'.format(req), timeout=10).text
    if response:
        return response
    else:
        return "lalala"

@itchat.msg_register(itchat.content.TEXT, isFriendChat=isFriendChat, isGroupChat=isGroupChat, isMpChat=isMpChat)
def xiaob(msg):
    # global toUserName
    time.sleep(1)
    # print('发送给:{}'.format(toUserName))
    if msg['FromUserName'] == itchat.search_mps(name='小冰')[0]['UserName']:
        # if toUserName:
        #     print(msg['Text'])
        #     itchat.send(msg['Text'], toUserName=toUserName)
        # else:
        #     print('Nnnn')
        response = get_response(msg['Text'])
        itchat.send(response, toUserName=itchat.search_mps(name='小冰')[0]['UserName'])
    # else:
    #     toUserName = msg['FromUserName']
    #     itchat.send(msg['Text'], toUserName=itchat.search_mps(name='小冰')[0]['UserName'])


itchat.auto_login()
itchat.run()