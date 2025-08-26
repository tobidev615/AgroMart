from typing import Any, Optional, Callable
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def cache_key_generator(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from function arguments."""
    # Create a string representation of args and kwargs
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = "|".join(key_parts)
    
    # Create a hash of the key string
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_view(timeout: int = 300, key_prefix: str = "view") -> Callable:
    """Decorator to cache view responses."""
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{cache_key_generator(*args, **kwargs)}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Call the view function
            response = view_func(*args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> None:
    """Invalidate all cache keys matching a pattern."""
    # Note: This is a simplified implementation
    # In production, you might want to use Redis SCAN or similar
    cache.clear()


def cache_model_queryset(model_class: Any, timeout: int = 300) -> Callable:
    """Decorator to cache model queryset results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key based on model and function
            cache_key = f"model:{model_class.__name__}:{func.__name__}:{cache_key_generator(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call the function
            result = func(*args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class CacheManager:
    """Utility class for managing cache operations."""
    
    @staticmethod
    def get_or_set(key: str, default_func: Callable, timeout: int = 300) -> Any:
        """Get from cache or set if not exists."""
        result = cache.get(key)
        if result is None:
            result = default_func()
            cache.set(key, result, timeout)
        return result
    
    @staticmethod
    def delete_pattern(pattern: str) -> None:
        """Delete cache keys matching pattern."""
        # This is a simplified implementation
        # In production, use Redis SCAN
        cache.clear()
    
    @staticmethod
    def get_user_cache_key(user_id: int, prefix: str) -> str:
        """Generate cache key for user-specific data."""
        return f"user:{user_id}:{prefix}"
    
    @staticmethod
    def invalidate_user_cache(user_id: int) -> None:
        """Invalidate all cache for a specific user."""
        pattern = f"user:{user_id}:*"
        CacheManager.delete_pattern(pattern)


# Cache keys for common operations
class CacheKeys:
    """Predefined cache keys for common operations."""
    
    @staticmethod
    def public_produce_list(filters: dict) -> str:
        """Cache key for public produce list."""
        filter_str = json.dumps(filters, sort_keys=True)
        return f"public_produce_list:{hashlib.md5(filter_str.encode()).hexdigest()}"
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        """Cache key for user profile."""
        return f"user_profile:{user_id}"
    
    @staticmethod
    def subscription_plans() -> str:
        """Cache key for subscription plans."""
        return "subscription_plans"
    
    @staticmethod
    def farmer_produce(farmer_id: int) -> str:
        """Cache key for farmer's produce."""
        return f"farmer_produce:{farmer_id}"


