import redis


def get_redis_conn(host, port, db):
    print('~~~~~~~~~~~~~~连接到redis~~~~~~~~~~~~~~~~~~~')
    return redis.StrictRedis(host=host, port=port, db=db)