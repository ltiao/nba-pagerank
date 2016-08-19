import os

REQUESTS_CACHE_BACKEND = os.environ.get('REQUESTS_CACHE_BACKEND', 'sqlite')

REDIS_HOST = os.environ['REDIS_MASTER_SERVICE_HOST'] \
          if os.environ.get('GET_HOSTS_FROM', '') == 'env' else 'redis-master'
REDIS_PORT = 6379
