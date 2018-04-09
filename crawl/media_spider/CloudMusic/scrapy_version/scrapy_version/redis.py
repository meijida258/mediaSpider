import redis
from .settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class ConnectRedis:
    def get_redis_conn(self, db):
        return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=db, decode_responses=True)

if __name__ == '__main__':
    conn_reds = ConnectRedis()
else:
    conn_reds = ConnectRedis()