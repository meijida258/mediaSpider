from http.server import HTTPServer, BaseHTTPRequestHandler
import io, shutil

save_path = ''
class MyHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        r_str = "Hello World"
        enc = "UTF-8"
        encoded = ''.join(r_str).encode(enc)
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)

    # def GET(self, params_dict):
    #     if params_dict['type'] == '注册':



httpd = HTTPServer(('', 8080), MyHttpHandler)
print("Server started on 127.0.0.1,port 8080.....")
httpd.serve_forever()  