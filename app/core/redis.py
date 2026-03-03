import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


def cache_user(user: dict, ttl=3600):
    key = f"user:{user['id']}"
    value = json.dumps(user)
    redis_client.set(key, value, ex=ttl)


def get_cached_user(user_id):
    key = f"user:{user_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def expire_cached_user(user_id):
    key = f"user:{user_id}"
    redis_client.delete(key)