'''
    本地的web服务器，处理其它程序获取代理的请求
    get http://localhost:6324/proxy_get 获取一个有效ip
    get http://localhost:6324/proxy_get?count=m 获取m个有效ip
    get http://localhost:6324/proxy_get?count=m&score=n 获取m个分数大于n的有效ip
'''
import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from http.server import HTTPServer, BaseHTTPRequestHandler# 启动服务函数
import re
import json
import redis
import random

# 自定义处理程序，用于处理HTTP请求
class TestHTTPHandler(BaseHTTPRequestHandler):
    # 处理GET请求
    def do_GET(self):
        # 正则匹配获得请求参数
        # 转成json，在编码成utf-8
        result_json = r.pop()
        proxies_json = json.dumps(result_json).encode('utf-8')
        print(proxies_json)
        # self.protocal_version = 'HTTP/1.1'  # 设置协议版本
        self.send_response(200)  # 设置响应状态码
        self.send_header('Content-Type', 'application/json')  # 设置响应头
        self.end_headers()
        self.wfile.write(proxies_json)  # 输出响应内容

def start_server(port):
    http_server = HTTPServer(('localhost', int(port)), TestHTTPHandler)
    http_server.serve_forever()  # 设置一直监听并接收请求


# print(type(json.dumps([{'123.1.1.1:123': '12'}, {'192.168.2.100:8081': '99'}])))
r = [{'code':200, '1':1},{'code':1, '1':'sss'}, {'code':1, '1':'sss'}, {'code':1, '1':'sss'}]
# start_server(1234)  # 启动服务，监听8000端口

print('{0}{0}'.format(2))