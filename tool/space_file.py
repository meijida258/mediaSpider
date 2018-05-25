import random
import re
import redis, json
import requests
import string

redis_conn = redis.StrictRedis('localhost', 6379)

for i in range(6,11):
    redis_conn.lpush('cloudmusic:start_urls', 'http://127.0.0.1:24423/{}'.format(i))