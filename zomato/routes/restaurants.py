from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantWithMenu, 
    MenuItemCreate, MenuItemResponse, RestaurantAnalytics, RestaurantWithReviews
)
import crud
from utils.business_logic import search_restaurants, get_trending_restaurants

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(restaurant: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    """Create a new restaurant"""
    try:
        return await crud.create_restaurant(db=db, restaurant=restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/", response_model=List[RestaurantResponse])
async def read_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all restaurants with pagination"""
    return await crud.get_restaurants(db, skip=skip, limit=limit)

@router.get("/active", response_model=List[RestaurantResponse])
async def read_active_restaurants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get only active restaurants"""
    return await crud.get_active_restaurants(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[RestaurantResponse])
async def search_restaurants_advanced(
    cuisine: Optional[str] = Query(None, description="Cuisine type to search for"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    location: Optional[str] = Query(None, description="Location to search in"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Advanced restaurant search with multiple filters"""
    return await search_restaurants(
        db, cuisine=cuisine, min_rating=min_rating, location=location, 
        skip=skip, limit=limit
    )

@router.get("/trending", response_model=List[dict])
async def get_trending_restaurants_endpoint(
    limit: int = Query(10, ge=1, le=50, description="Number of trending restaurants to return"),
    days: int = Query(7, ge=1, le=30, description="Number of days to consider for trending"),
    db: AsyncSession = Depends(get_db)
):
    """Get trending restaurants based on recent order activity"""
    return await get_trending_restaurants(db, limit=limit, days=days)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def read_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific restaurant by ID"""
    db_restaurant = await crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@router.get("/{restaurant_id}/with-menu", response_model=RestaurantWithMenu)
async def read_restaurant_with_menu(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Get restaurant with all menu items"""
    db_restaurant = await crud.get_restaurant_with_menu(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@router.get("/{restaurant_id}/menu", response_model=List[MenuItemResponse])
async def read_restaurant_menu(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items for a restaurant"""
    # First check if restaurant exists
    db_restaurant = await crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return await crud.get_restaurant_menu_items(db, restaurant_id=restaurant_id, skip=skip, limit=limit)

@router.post("/{restaurant_id}/menu-items/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant_menu_item(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add menu item to restaurant"""
    # Override restaurant_id from URL
    menu_item.restaurant_id = restaurant_id
    try:
        return await crud.create_menu_item(db=db, menu_item=menu_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: int, 
    restaurant: RestaurantUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a restaurant"""
    try:
        db_restaurant = await crud.update_restaurant(db, restaurant_id=restaurant_id, restaurant_update=restaurant)
        if db_restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return db_restaurant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/{restaurant_id}", response_model=RestaurantResponse)
async def delete_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a restaurant"""
    db_restaurant = await crud.delete_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

@router.get("/{restaurant_id}/reviews", response_model=List[dict])
async def get_restaurant_reviews(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of reviews to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews for a restaurant"""
    # Check if restaurant exists
    restaurant = await crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    reviews = await crud.get_restaurant_reviews(db, restaurant_id, skip=skip, limit=limit)
    return reviews

@router.get("/{restaurant_id}/analytics", response_model=RestaurantAnalytics)
async def get_restaurant_analytics(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive performance metrics for a restaurant"""
    # Check if restaurant exists
    restaurant = await crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    analytics = await crud.get_restaurant_analytics(db, restaurant_id)
    return analytics