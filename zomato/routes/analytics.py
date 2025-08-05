from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import RestaurantAnalytics, CustomerAnalytics
import crud

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/restaurants/{restaurant_id}", response_model=RestaurantAnalytics)
async def get_restaurant_analytics(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive performance metrics for a restaurant"""
    # Check if restaurant exists
    restaurant = await crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    try:
        analytics = await crud.get_restaurant_analytics(db, restaurant_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@router.get("/customers/{customer_id}", response_model=CustomerAnalytics)
async def get_customer_analytics(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive order analytics for a customer"""
    # Check if customer exists
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        analytics = await crud.get_customer_analytics(db, customer_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate analytics")