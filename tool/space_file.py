import requests
import redis
from selenium import webdriver
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = 'cjljc'
db =2
reds = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=db)
print(reds.scard('wait_visit_music'))