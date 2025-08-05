#!/usr/bin/env python3
"""
Setup script for Redis caching in Zomato API
This script helps verify Redis installation and connection
"""

import asyncio
import sys
import redis.asyncio as redis
from database import init_cache, get_redis

async def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("🔄 Testing Redis connection...")
    
    try:
        # Initialize cache
        redis_client = await init_cache()
        
        if not redis_client:
            print("❌ Failed to initialize Redis client")
            return False
        
        # Test basic operations
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        
        if value == "test_value":
            print("✅ Redis connection successful!")
            print(f"   Redis client: {redis_client}")
            
            # Clean up test key
            await redis_client.delete("test_key")
            
            # Get Redis info
            info = await redis_client.info()
            print(f"   Redis version: {info.get('redis_version', 'Unknown')}")
            print(f"   Memory usage: {info.get('used_memory_human', 'Unknown')}")
            
            return True
        else:
            print("❌ Redis read/write test failed")
            return False
            
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        print("   Make sure Redis server is running:")
        print("   - Install Redis: brew install redis (macOS) or apt-get install redis-server (Ubuntu)")
        print("   - Start Redis: redis-server")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    """Main setup function"""
    print("🚀 Zomato API Redis Cache Setup")
    print("=" * 40)
    
    # Test Redis connection
    redis_ok = await test_redis_connection()
    
    if redis_ok:
        print("\n✅ Redis setup complete!")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Create sample data: POST /cache/demo/sample-data")
        print("3. Test caching: GET /cache/demo/cache-test/1")
        print("4. Monitor cache: GET /cache/stats")
        print("\nAPI Documentation: http://localhost:8000/docs")
    else:
        print("\n❌ Redis setup failed!")
        print("Please ensure Redis is installed and running before starting the application.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())