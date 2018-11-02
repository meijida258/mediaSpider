import asyncio
from aiohttp import web
import random

def home(request):
    cal = request.GET.get('cal', '').strip()
    print('received calculate is {}'.format(cal))
    if cal:
        res = int(cal)**2
    else:
        res = 404
    return web.Response(content_type='text/html',text=str(res))

async def init(loop, address, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET','/', home)
    handler = app.make_handler()
    server = await loop.create_server(handler,
                                      address, port)
    return server.sockets[0]

def main(address='127.0.0.1', port=2384):
    loop = asyncio.get_event_loop()
    host = loop.run_until_complete(init(loop, address, port))
    print('server runs on {}'.format(host))
    try:
        loop.run_forever()
    except Exception:
        pass
    loop.close()

if __name__ == '__main__':
    main()