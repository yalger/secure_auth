from ipaddress import ip_network

from app.core.redis import redis_client

def check_rate_limit(key: str, limit: int, window: int) -> bool:
    """
    Check if the rate limit has been exceeded for a given key.

    :param key: The key to check the rate limit for.
    :param limit: The maximum number of requests allowed.
    :param window: The time window in seconds.
    :return: True if the rate limit has not been exceeded, False otherwise.
    """

    count = redis_client.get(key)
    if count and int(count) >= limit:
        return False

    pipe = redis_client.pipeline()

    pipe.incr(key)

    if not count:
        pipe.expire(key, window)

    pipe.execute()

    return True

def check_login_rate_limit(ip: str, username: str) -> bool:

    ip_key = f"login:ip:{ip}"
    user_key = f"login:user:{username}"
    ip_user_key = f"login:ip_user:{ip}:{username}"

    # IP limit
    if not check_rate_limit(ip_key, limit=30, window=60):  # 30 requests per minute
        return False

    # User limit
    if not check_rate_limit(user_key, limit=5, window=60):  # 5 requests per minute
        return False

    # IP-User combination limit
    if not check_rate_limit(ip_user_key, limit=3, window=60):  # 3 requests per minute
        return False

    return True

def clear_login_attempts(ip: str, username: str):

    redis_client.delete(f"login:ip:{ip}")
    redis_client.delete(f"login:user:{username}")
    redis_client.delete(f"login:ip_user:{ip}:{username}")