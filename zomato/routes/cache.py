"""
Cache management endpoints for Redis caching
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from database import get_db
from utils.cache_utils import (
    get_cache_stats, 
    cache_clear_all, 
    cache_clear_namespace,
    CACHE_NAMESPACES
)
import crud
from schemas import RestaurantCreate
from datetime import time

router = APIRouter(prefix="/cache", tags=["cache"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_statistics():
    """
    Get comprehensive cache statistics including:
    - Redis connection info
    - Total cache keys
    - Keys by namespace
    - TTL settings
    """
    try:
        stats = await get_cache_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )

@router.delete("/clear")
async def clear_entire_cache():
    """
    Clear the entire Redis cache
    WARNING: This will remove all cached data
    """
    try:
        deleted_count = await cache_clear_all()
        return {
            "status": "success",
            "message": "Successfully cleared entire cache",
            "deleted_keys": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.delete("/clear/restaurants")
async def clear_restaurant_cache():
    """
    Clear only restaurant-related caches
    This includes all restaurant listings, details, and search results
    """
    try:
        deleted_count = await cache_clear_namespace("restaurants")
        return {
            "status": "success",
            "message": "Successfully cleared restaurant cache namespace",
            "deleted_keys": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear restaurant cache: {str(e)}"
        )

@router.delete("/clear/{namespace}")
async def clear_namespace_cache(namespace: str):
    """
    Clear cache for a specific namespace
    Available namespaces: restaurants, menu_items, customers, orders, reviews
    """
    if namespace not in CACHE_NAMESPACES.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid namespace. Available namespaces: {list(CACHE_NAMESPACES.values())}"
        )
    
    try:
        deleted_count = await cache_clear_namespace(namespace)
        return {
            "status": "success",
            "message": f"Successfully cleared {namespace} cache namespace",
            "deleted_keys": deleted_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear {namespace} cache: {str(e)}"
        )

@router.get("/demo/cache-test/{restaurant_id}")
async def demonstrate_cache_performance(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """
    Demonstrate cache performance by fetching restaurant details
    First request will be CACHE MISS, subsequent requests will be CACHE HIT
    Check logs to see performance differences
    """
    try:
        # This will use the cached version of the restaurant endpoint
        restaurant = await crud.get_restaurant(db, restaurant_id=restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        return {
            "status": "success",
            "message": "Check server logs for cache hit/miss information and response times",
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "note": "First request = CACHE MISS (slower), Subsequent requests = CACHE HIT (faster)"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache test failed: {str(e)}"
        )

@router.post("/demo/sample-data")
async def create_sample_restaurants(db: AsyncSession = Depends(get_db)):
    """
    Create sample restaurant data for testing cache functionality
    This will create 10 sample restaurants with different cuisines
    """
    try:
        sample_restaurants = [
            {
                "name": "Spice Garden Indian Restaurant",
                "description": "Authentic Indian cuisine with traditional spices and flavors",
                "cuisine_type": "Indian",
                "address": "123 Curry Lane, Spice District, Mumbai",
                "phone_number": "+91-9876543210",
                "opening_time": "11:00",
                "closing_time": "23:00"
            },
            {
                "name": "Dragon Palace Chinese Kitchen",
                "description": "Traditional Chinese dishes with modern presentation",
                "cuisine_type": "Chinese",
                "address": "456 Dragon Street, Chinatown, Delhi",
                "phone_number": "+91-9876543211",
                "opening_time": "12:00",
                "closing_time": "22:30"
            },
            {
                "name": "Mama Mia Italian Bistro",
                "description": "Authentic Italian pasta, pizza, and wine selection",
                "cuisine_type": "Italian",
                "address": "789 Pizza Plaza, Little Italy, Bangalore",
                "phone_number": "+91-9876543212",
                "opening_time": "10:30",
                "closing_time": "23:30"
            },
            {
                "name": "Tokyo Sushi Express",
                "description": "Fresh sushi and Japanese cuisine prepared by expert chefs",
                "cuisine_type": "Japanese",
                "address": "321 Sushi Street, Japan Town, Pune",
                "phone_number": "+91-9876543213",
                "opening_time": "11:30",
                "closing_time": "22:00"
            },
            {
                "name": "Le Petit Café French",
                "description": "Elegant French cuisine with wine pairings",
                "cuisine_type": "French",
                "address": "654 Baguette Boulevard, French Quarter, Chennai",
                "phone_number": "+91-9876543214",
                "opening_time": "09:00",
                "closing_time": "21:00"
            },
            {
                "name": "Taco Fiesta Mexican Grill",
                "description": "Vibrant Mexican flavors with fresh ingredients",
                "cuisine_type": "Mexican",
                "address": "987 Salsa Street, Mexican Village, Hyderabad",
                "phone_number": "+91-9876543215",
                "opening_time": "11:00",
                "closing_time": "24:00"
            },
            {
                "name": "Mediterranean Olive Garden",
                "description": "Healthy Mediterranean dishes with olive oil and herbs",
                "cuisine_type": "Mediterranean",
                "address": "147 Olive Avenue, Med Coast, Kolkata",
                "phone_number": "+91-9876543216",
                "opening_time": "10:00",
                "closing_time": "22:00"
            },
            {
                "name": "Bangkok Street Thai Kitchen",
                "description": "Spicy and flavorful Thai street food experience",
                "cuisine_type": "Thai",
                "address": "258 Pad Thai Lane, Thai Town, Ahmedabad",
                "phone_number": "+91-9876543217",
                "opening_time": "12:00",
                "closing_time": "23:00"
            },
            {
                "name": "Seoul BBQ Korean House",
                "description": "Korean BBQ and traditional dishes with authentic flavors",
                "cuisine_type": "Korean",
                "address": "369 Kimchi Road, Korea Street, Jaipur",
                "phone_number": "+91-9876543218",
                "opening_time": "17:00",
                "closing_time": "01:00"
            },
            {
                "name": "Burger Junction American Diner",
                "description": "Classic American burgers, fries, and milkshakes",
                "cuisine_type": "American",
                "address": "741 Burger Blvd, American Corner, Lucknow",
                "phone_number": "+91-9876543219",
                "opening_time": "10:00",
                "closing_time": "23:30"
            }
        ]
        
        created_restaurants = []
        
        for restaurant_data in sample_restaurants:
            try:
                # Convert time strings to time objects
                restaurant_data["opening_time"] = time.fromisoformat(restaurant_data["opening_time"])
                restaurant_data["closing_time"] = time.fromisoformat(restaurant_data["closing_time"])
                
                restaurant_create = RestaurantCreate(**restaurant_data)
                restaurant = await crud.create_restaurant(db=db, restaurant=restaurant_create)
                created_restaurants.append({
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "cuisine_type": restaurant.cuisine_type
                })
            except ValueError:
                # Skip if restaurant already exists
                continue
        
        return {
            "status": "success",
            "message": f"Successfully created {len(created_restaurants)} sample restaurants",
            "created_restaurants": created_restaurants,
            "note": "Some restaurants may have been skipped if they already exist"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sample data: {str(e)}"
        )