from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import RestaurantCreate, RestaurantUpdate, RestaurantResponse
import crud

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
async def search_restaurants(
    cuisine: str = Query(..., min_length=1, description="Cuisine type to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search restaurants by cuisine type"""
    return await crud.search_restaurants_by_cuisine(db, cuisine_type=cuisine, skip=skip, limit=limit)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def read_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific restaurant by ID"""
    db_restaurant = await crud.get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant

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