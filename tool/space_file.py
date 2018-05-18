import requests

headers = {
        'host': 'music.163.com',
        'Referer': 'http://music.163.com/search/',
        'User-Agent':
        ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')
        }
cookies = {'appver': '1.5.2'}

def get_artists_songlist(artist_id):
    url = 'http://music.163.com/api/artist/{}'.format(artist_id)

    r = requests.get(url, headers=headers, cookies=cookies)
    hotSongs = r.json()['hotSongs']
    return hotSongs

# print(get_artists_songlist(1876))
# for key, value in headers.items():
#     print('{}:{}'.format(key, value))
# print(list(["39.137.77.68:80"]))
import time
st = time.clock()
print(requests.get('http://localhost:6324/proxy_get?count=1&score=30').json()[0])
print(time.clock() - st)