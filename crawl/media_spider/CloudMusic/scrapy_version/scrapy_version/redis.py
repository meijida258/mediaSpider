import redis
from .settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


def get_redis_conn(db):
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=db, password=REDIS_PASSWORD)