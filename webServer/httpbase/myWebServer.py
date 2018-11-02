'''
    本地的web服务器，处理其它程序获取代理的请求
    get http://localhost:6324/proxy_get 获取一个有效ip
    get http://localhost:6324/proxy_get?count=m 获取m个有效ip
    get http://localhost:6324/proxy_get?count=m&score=n 获取m个分数大于n的有效ip
'''
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import json
import redis
import random, string
import time

# 自定义处理程序，用于处理HTTP请求
class TestHTTPHandler(BaseHTTPRequestHandler):
    # 处理GET请求
    # redis_conn = redis.StrictRedis(host='localhost', port=6379, db=3)
    def do_GET(self):
        # 正则匹配获得请求参数
        if re.match(r'(/\d+)', self.path):

            self.send_response(200)  # 设置响应状态码
            self.send_header('Content-Type', 'text/html')  # 设置响应头

            self.end_headers()
            self.wfile.write(''.format(int(self.path)**2).encode('utf-8'))  # 输出响应内容
        else:
            self.send_error(406)  # 设置响应状态码
            # self.wfile.write(json.dumps(result).encode('utf-8'))  # 输出响应内容

def start_server(port):
    http_server = HTTPServer(('localhost', int(port)), TestHTTPHandler)
    http_server.serve_forever()  # 设置一直监听并接收请求


# print(type(json.dumps([{'123.1.1.1:123': '12'}, {'192.168.2.100:8081': '99'}])))
start_server(24423)  # 启动服务，监听8000端口