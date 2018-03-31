import ipaddress

try:
    ip = ipaddress.ip_address('192.168.1.119')
    print(ip.packed)
except Exception as e:
    print(e)

print(ipaddress.ip_address(3221225985))