"""
Cache utility functions for Redis caching implementation
"""
import time
import logging
from typing import Any, Optional
from functools import wraps
from database import get_redis
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache namespaces
CACHE_NAMESPACES = {
    "restaurants": "restaurants",
    "menu_items": "menu_items",
    "customers": "customers",
    "orders": "orders",
    "reviews": "reviews"
}

# Cache TTL settings (in seconds)
CACHE_TTL = {
    "restaurants_list": 300,      # 5 minutes
    "restaurant_detail": 600,     # 10 minutes
    "restaurant_search": 180,     # 3 minutes
    "active_restaurants": 240,    # 4 minutes
    "restaurant_menu": 360,       # 6 minutes
    "trending_restaurants": 120   # 2 minutes
}

def get_cache_key(namespace: str, key: str) -> str:
    """Generate cache key with namespace"""
    return f"zomato-cache:{namespace}:{key}"

async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    redis_client = get_redis()
    if not redis_client:
        return None
    
    try:
        cached_value = await redis_client.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        logger.error("Cache get error for key %s: %s", key, e)
        return None

async def cache_set(key: str, value: Any, ttl: int) -> bool:
    """Set value in cache with TTL"""
    redis_client = get_redis()
    if not redis_client:
        return False
    
    try:
        serialized_value = json.dumps(value, default=str)
        await redis_client.setex(key, ttl, serialized_value)
        return True
    except Exception as e:
        logger.error("Cache set error for key %s: %s", key, e)
        return False

async def cache_delete(key: str) -> bool:
    """Delete specific key from cache"""
    redis_client = get_redis()
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error("Cache delete error for key %s: %s", key, e)
        return False

async def cache_clear_namespace(namespace: str) -> int:
    """Clear all keys in a namespace"""
    redis_client = get_redis()
    if not redis_client:
        return 0
    
    try:
        pattern = f"zomato-cache:{namespace}:*"
        keys = await redis_client.keys(pattern)
        if keys:
            deleted_count = await redis_client.delete(*keys)
            logger.info("Cleared %d keys from namespace %s", deleted_count, namespace)
            return deleted_count
        return 0
    except Exception as e:
        logger.error("Cache clear namespace error for %s: %s", namespace, e)
        return 0

async def cache_clear_all() -> int:
    """Clear entire cache"""
    redis_client = get_redis()
    if not redis_client:
        return 0
    
    try:
        keys = await redis_client.keys("zomato-cache:*")
        if keys:
            deleted_count = await redis_client.delete(*keys)
            logger.info("Cleared entire cache: %d keys", deleted_count)
            return deleted_count
        return 0
    except Exception as e:
        logger.error("Cache clear all error: %s", e)
        return 0

async def get_cache_stats() -> dict:
    """Get cache statistics"""
    redis_client = get_redis()
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        info = await redis_client.info()
        keys = await redis_client.keys("zomato-cache:*")
        
        # Group keys by namespace
        namespace_counts = {}
        for key in keys:
            if isinstance(key, str):
                parts = key.split(":")
                if len(parts) >= 3:
                    namespace = parts[2]
                    namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
        
        return {
            "redis_info": {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_keys": len(keys)
            },
            "cache_keys": {
                "total": len(keys),
                "by_namespace": namespace_counts
            },
            "cache_namespaces": list(CACHE_NAMESPACES.values()),
            "ttl_settings": CACHE_TTL
        }
    except Exception as e:
        logger.error("Cache stats error: %s", e)
        return {"error": str(e)}

def cache_response(namespace: str, ttl_key: str, key_func=None):
    """
    Decorator for caching API responses
    
    Args:
        namespace: Cache namespace
        ttl_key: Key to lookup TTL in CACHE_TTL dict
        key_func: Function to generate cache key from function arguments
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_suffix = key_func(*args, **kwargs)
            else:
                # Default key generation from function name and args
                cache_key_suffix = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            cache_key = get_cache_key(namespace, cache_key_suffix)
            ttl = CACHE_TTL.get(ttl_key, 300)
            
            # Record start time for performance logging
            start_time = time.time()
            
            # Try to get from cache
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                logger.info("CACHE HIT - %s - Key: %s - Response time: %.2fms", func.__name__, cache_key, response_time)
                return cached_result
            
            # Cache miss - execute function
            logger.info("CACHE MISS - %s - Key: %s", func.__name__, cache_key)
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_set(cache_key, result, ttl)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            logger.info("CACHE MISS PROCESSED - %s - Response time: %.2fms", func.__name__, response_time)
            
            return result
        return wrapper
    return decorator

async def invalidate_restaurant_cache(restaurant_id: Optional[int] = None):
    """
    Invalidate restaurant-related caches
    
    Args:
        restaurant_id: If provided, invalidate specific restaurant caches
    """
    redis_client = get_redis()
    if not redis_client:
        return
    
    try:
        # Always clear list caches when any restaurant is modified
        list_patterns = [
            "zomato-cache:restaurants:read_restaurants_*",
            "zomato-cache:restaurants:read_active_restaurants_*",
            "zomato-cache:restaurants:search_restaurants_*",
            "zomato-cache:restaurants:get_trending_restaurants_*"
        ]
        
        for pattern in list_patterns:
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)
                logger.info("Invalidated %d keys matching pattern: %s", len(keys), pattern)
        
        # If specific restaurant ID provided, clear its individual caches
        if restaurant_id:
            specific_patterns = [
                f"zomato-cache:restaurants:read_restaurant_{restaurant_id}",
                f"zomato-cache:restaurants:read_restaurant_with_menu_{restaurant_id}",
                f"zomato-cache:restaurants:read_restaurant_menu_{restaurant_id}_*"
            ]
            
            for pattern in specific_patterns:
                if "*" in pattern:
                    keys = await redis_client.keys(pattern)
                    if keys:
                        await redis_client.delete(*keys)
                else:
                    await redis_client.delete(pattern)
            
            logger.info("Invalidated caches for restaurant ID: %s", restaurant_id)
    
    except Exception as e:
        logger.error("Cache invalidation error: %s", e)