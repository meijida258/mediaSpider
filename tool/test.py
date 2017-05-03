import socket, sys
url = 'www.baidu.com'
port = 80
sock = socket.socket()

sock.connect((url, port))

try:
    sock.send(('GET {} HTTP/1.1\r\nHost: localhost\r\n\r\n'.format(url)).encode())
except Exception as e:
    print(e)
    sys.exit()
reply = sock.recv(4096)
print(reply)