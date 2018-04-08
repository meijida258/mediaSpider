import redis
from .settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

class ConnectRedis:
    def get_redis_conn(self, db):
        reds_url = 'redis://{}@{}:{}/{}'.format(REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, db)
        return redis.from_url(reds_url)

if __name__ == '__main__':
    conn_reds = ConnectRedis()
else:
    conn_reds = ConnectRedis()