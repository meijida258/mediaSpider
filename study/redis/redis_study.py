import redis

reds = redis.Redis(host="localhost", port=6379, db=2, password='cjljc', decode_responses=True)
print(reds.get('name:cjldd'))
reds.set('name', 'cjldd')

reds_keys = reds.keys()
print(reds_keys)