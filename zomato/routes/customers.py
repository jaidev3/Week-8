from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithOrders,
    CustomerAnalytics
)
import crud

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer"""
    try:
        # Check if customer with email already exists
        existing_customer = await crud.get_customer_by_email(db, customer.email)
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this email already exists")
        
        db_customer = await crud.create_customer(db, customer)
        return db_customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0, description="Number of customers to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of customers to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all customers with pagination"""
    customers = await crud.get_customers(db, skip=skip, limit=limit)
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a customer by ID"""
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a customer"""
    try:
        # Check if customer exists
        existing_customer = await crud.get_customer(db, customer_id)
        if not existing_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Check email uniqueness if email is being updated
        if customer_update.email and customer_update.email != existing_customer.email:
            email_customer = await crud.get_customer_by_email(db, customer_update.email)
            if email_customer:
                raise HTTPException(status_code=400, detail="Customer with this email already exists")
        
        updated_customer = await crud.update_customer(db, customer_id, customer_update)
        return updated_customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer"""
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    await crud.delete_customer(db, customer_id)
    return {"message": "Customer deleted successfully"}

@router.get("/{customer_id}/orders", response_model=List[dict])
async def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of orders to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific customer"""
    # Check if customer exists
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    orders = await crud.get_customer_orders(db, customer_id, skip=skip, limit=limit)
    return orders

@router.get("/{customer_id}/reviews", response_model=List[dict])
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

@router.get("/{customer_id}/analytics", response_model=CustomerAnalytics)
async def get_customer_analytics(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics for a customer"""
    # Check if customer exists
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    analytics = await crud.get_customer_analytics(db, customer_id)
    return analytics