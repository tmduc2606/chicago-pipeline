import functools
import hashlib
import json
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis


def cached(ttl: int = 300) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, redis: Redis | None = None, **kwargs: Any) -> Any:
            if redis is None:
                return await func(*args, **kwargs)
            key_parts = [func.__name__]
            for a in args[1:]:
                key_parts.append(str(a))
            for k, v in sorted(kwargs.items()):
                if k == "redis":
                    continue
                key_parts.append(f"{k}={v}")
            cache_key = f"api:{hashlib.sha256(':'.join(key_parts).encode()).hexdigest()}"
            cached_val = await redis.get(cache_key)
            if cached_val:
                return json.loads(cached_val)
            result = await func(*args, **kwargs)
            serializable = _to_dict(result)
            await redis.setex(cache_key, ttl, json.dumps(serializable, default=str))
            return result
        return wrapper
    return decorator


def _to_dict(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    return obj
