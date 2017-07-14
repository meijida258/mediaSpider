# import SimpleHTTPServer
# import SocketServer
# import re
#
#
# def htc(m):
#     return chr(int(m.group(1), 16))
#
#
# def urldecode(url):
#     rex = re.compile('%([0-9a-hA-H][0-9a-hA-H])', re.M)
#     return rex.sub(htc, url)
#
#
# class SETHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
#     def createHTML(self, return_result=None):
#         html = file("index.html", "r")
#         for line in html:
#             self.wfile.write(line)
#         if return_result:
#             self.wfile.write(return_result)
#     def do_GET(self):
#         print ("GET")
#         self.createHTML()
#
#     def do_POST(self):
#         print ("POST")
#         length = int(self.headers.getheader('content-length'))
#         qs = self.rfile.read(length)
#         url = urldecode(qs)
#         print url
#         result = self.identify(url)
#         if result:
#             self.createHTML(result)
#         else:
#             self.createHTML()
#
#     def identify(self, receipt_str):
#         result = receipt_str.split('&')
#         search_key = result[0] + '&' + result[-1]
#         if result[1] == 'login':
#             with open('userlist.txt', 'r') as fl:
#                 fl_content = fl.readlines()
#                 for each_lines in fl_content:
#                     if each_lines.find(search_key) >= 0:
#                         fl.close()
#                         return 'login success'
#                 fl.close()
#                 return 'login failed'
#         else:
#             with open('userlist.txt', 'r') as fl:
#                 fl_content = fl.readlines()
#                 for each_lines in fl_content:
#                     if each_lines.find(search_key) >= 0:
#                         fl.close()
#                         return 'username exist'

# Handler = SETHandler
# PORT = 8080
# httpd = SocketServer.TCPServer(("", PORT), Handler)
# print ("serving at port", PORT)
# httpd.serve_forever()
from PIL import Image

a = Image.open('C:/Users/Administrator/Desktop/2.jpg')
out = a.resize((900,1200))
out.save('C:/Users/Administrator/Desktop/1.jpg')
