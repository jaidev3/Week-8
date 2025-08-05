# Zomato API - Redis Caching Implementation

## Overview
This implementation extends the Zomato food delivery API with Redis caching for improved performance. The caching system implements sophisticated cache management strategies with namespace-based organization and intelligent invalidation.

## Features Implemented

### 1. Redis Integration
- **Redis Server**: Configured with `redis==5.0.1`
- **FastAPI Cache**: Integrated with `fastapi-cache2==0.2.1`
- **Connection Management**: Async Redis client with connection pooling
- **Environment Configuration**: Configurable Redis URL via environment variables

### 2. Caching Strategy

#### Cache TTL Settings
- **Restaurant List**: 300 seconds (5 minutes)
- **Individual Restaurant**: 600 seconds (10 minutes)
- **Restaurant Search**: 180 seconds (3 minutes)
- **Active Restaurants**: 240 seconds (4 minutes)
- **Restaurant Menu**: 360 seconds (6 minutes)
- **Trending Restaurants**: 120 seconds (2 minutes)

#### Namespace Organization
- **restaurants**: All restaurant-related data
- **menu_items**: Menu item data
- **customers**: Customer data
- **orders**: Order data
- **reviews**: Review data

### 3. Cached Endpoints

#### Restaurant Endpoints with Caching:
- `GET /restaurants/` - List all restaurants (5-minute TTL)
- `GET /restaurants/active` - List active restaurants (4-minute TTL)
- `GET /restaurants/search` - Search restaurants (3-minute TTL)
- `GET /restaurants/trending` - Trending restaurants (2-minute TTL)
- `GET /restaurants/{id}` - Individual restaurant (10-minute TTL)
- `GET /restaurants/{id}/with-menu` - Restaurant with menu (10-minute TTL)
- `GET /restaurants/{id}/menu` - Restaurant menu items (6-minute TTL)

### 4. Cache Management Endpoints

#### Cache Statistics
```http
GET /cache/stats
```
Returns comprehensive cache statistics including:
- Redis connection info
- Total cache keys
- Keys by namespace
- TTL settings

#### Cache Clearing
```http
DELETE /cache/clear                    # Clear entire cache
DELETE /cache/clear/restaurants        # Clear restaurant namespace
DELETE /cache/clear/{namespace}        # Clear specific namespace
```

#### Demo Endpoints
```http
GET /cache/demo/cache-test/{restaurant_id}  # Demonstrate cache performance
POST /cache/demo/sample-data                # Create sample restaurants
```

### 5. Cache Invalidation Strategy

#### Automatic Invalidation Rules:
- **Restaurant Creation**: Clears entire restaurant namespace
- **Restaurant Update**: Clears specific restaurant cache + list caches
- **Restaurant Deletion**: Clears specific restaurant cache + list caches

#### Intelligent Key Management:
- List caches are cleared when any restaurant is modified
- Individual restaurant caches are cleared specifically
- Search result caches are invalidated on restaurant changes

### 6. Performance Monitoring

#### Response Time Logging:
- **CACHE HIT**: Logs response time (typically <10ms)
- **CACHE MISS**: Logs database query time
- **Performance Comparison**: Clear visibility of cache effectiveness

#### Log Examples:
```
INFO: CACHE HIT - read_restaurants - Key: zomato-cache:restaurants:read_restaurants_0_100 - Response time: 2.45ms
INFO: CACHE MISS - read_restaurant - Key: zomato-cache:restaurants:read_restaurant_1
INFO: CACHE MISS PROCESSED - read_restaurant - Response time: 156.78ms
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Redis Server
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Download from https://redis.io/download
```

### 3. Start Redis Server
```bash
redis-server
```

### 4. Configure Environment (Optional)
```bash
export REDIS_URL="redis://localhost:6379/0"
```

### 5. Start Application
```bash
python main.py
```

## Testing Cache Performance

### 1. Create Sample Data
```http
POST /cache/demo/sample-data
```

### 2. Test Cache Performance
```http
GET /cache/demo/cache-test/1
```
- First request: CACHE MISS (slower)
- Subsequent requests: CACHE HIT (faster)

### 3. Monitor Cache Statistics
```http
GET /cache/stats
```

### 4. Clear Caches for Testing
```http
DELETE /cache/clear/restaurants
```

## Cache Key Structure

### Key Format:
```
zomato-cache:{namespace}:{function_name}_{parameters}
```

### Examples:
- `zomato-cache:restaurants:read_restaurants_0_100`
- `zomato-cache:restaurants:read_restaurant_1`
- `zomato-cache:restaurants:search_restaurants_Indian_none_none_0_100`

## Performance Benefits

### Expected Performance Improvements:
- **Cache Hit Response Time**: <10ms
- **Database Query Reduction**: 80-90% for frequently accessed data
- **Server Load Reduction**: Significant reduction in database connections
- **Scalability**: Better handling of concurrent requests

### Cache Hit Scenarios:
- Repeated restaurant listings
- Individual restaurant details
- Search results for popular cuisines
- Menu browsing for popular restaurants

## Error Handling

### Redis Connection Issues:
- Graceful degradation when Redis is unavailable
- All endpoints continue to work without caching
- Error logging for monitoring and debugging

### Cache Failures:
- Non-blocking cache operations
- Automatic fallback to database queries
- Comprehensive error logging

## Monitoring & Maintenance

### Cache Statistics Monitoring:
- Total cache keys
- Memory usage
- Hit/miss ratios (via logs)
- Namespace distribution

### Cache Maintenance:
- Automatic TTL expiration
- Manual cache clearing capabilities
- Namespace-based selective clearing

## Architecture Benefits

### Scalability:
- Reduced database load
- Faster response times
- Better concurrent user handling

### Flexibility:
- Configurable TTL per endpoint type
- Namespace-based cache management
- Easy cache invalidation strategies

### Monitoring:
- Comprehensive performance logging
- Cache statistics endpoint
- Clear visibility into cache effectiveness

## Development Notes

### Cache Decorator Usage:
```python
@cache_response("restaurants", "restaurant_detail", 
                lambda restaurant_id, *args, **kwargs: f"read_restaurant_{restaurant_id}")
async def read_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    # Function implementation
```

### Cache Invalidation:
```python
# After restaurant modification
await invalidate_restaurant_cache(restaurant_id)
```

This implementation provides a robust, scalable caching solution that significantly improves API performance while maintaining data consistency through intelligent cache invalidation strategies.