from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import ReviewCreate, ReviewResponse
import crud

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/orders/{order_id}/review", response_model=ReviewResponse, status_code=201)
async def create_review(
    order_id: int,
    review: ReviewCreate,
    customer_id: int = Query(..., description="Customer ID creating the review"),
    db: AsyncSession = Depends(get_db)
):
    """Add a review for a completed order"""
    try:
        # Validate that customer exists
        customer = await crud.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Create the review
        db_review = await crud.create_review(db, customer_id, order_id, review)
        return db_review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/restaurants/{restaurant_id}/reviews", response_model=List[ReviewResponse])
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

@router.get("/customers/{customer_id}/reviews", response_model=List[ReviewResponse])
async def get_customer_reviews(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of reviews to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all reviews by a customer"""
    # Check if customer exists
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    reviews = await crud.get_customer_reviews(db, customer_id, skip=skip, limit=limit)
    return reviews