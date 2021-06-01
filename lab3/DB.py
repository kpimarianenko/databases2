import redis

connection = redis.Redis(charset='utf-8', decode_responses=True, port=6379)
