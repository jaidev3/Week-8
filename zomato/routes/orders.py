from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import (
    OrderCreate, OrderUpdate, OrderResponse, OrderWithDetails,
    OrderStatusEnum
)
from models import OrderStatus
import crud

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/customers/{customer_id}/orders", response_model=OrderResponse, status_code=201)
async def place_order(
    customer_id: int,
    order: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Place a new order for a customer"""
    try:
        # Validate that customer exists
        customer = await crud.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Validate that customer is active
        if not customer.is_active:
            raise HTTPException(status_code=400, detail="Customer account is inactive")
        
        # Create the order
        db_order = await crud.create_order(db, customer_id, order)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{order_id}", response_model=OrderWithDetails)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get order with full details including customer, restaurant, and items"""
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update order status and other fields"""
    # Check if order exists
    existing_order = await crud.get_order(db, order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate status transitions
    if order_update.order_status:
        current_status = existing_order.order_status
        new_status = OrderStatus(order_update.order_status.value)
        
        # Define valid status transitions
        valid_transitions = {
            OrderStatus.PLACED: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED],
            OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Final state
            OrderStatus.CANCELLED: []   # Final state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status transition from {current_status.value} to {new_status.value}"
            )
    
    try:
        updated_order = await crud.update_order_status(db, order_id, order_update)
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/customers/{customer_id}/orders", response_model=List[OrderResponse])
async def get_customer_orders(
    customer_id: int,
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of orders to return"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    db: AsyncSession = Depends(get_db)
):
    """Get customer's order history with optional status filtering"""
    # Check if customer exists
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if status:
        # Get orders filtered by status
        order_status = OrderStatus(status.value)
        orders = await crud.get_orders_by_status(db, order_status, skip=skip, limit=limit)
        # Filter by customer
        orders = [order for order in orders if order.customer_id == customer_id]
    else:
        orders = await crud.get_customer_orders(db, customer_id, skip=skip, limit=limit)
    
    return orders

@router.get("/restaurants/{restaurant_id}/orders", response_model=List[OrderResponse])
async def get_restaurant_orders(
    restaurant_id: int,
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of orders to return"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    db: AsyncSession = Depends(get_db)
):
    """Get restaurant's orders with optional status filtering"""
    # Check if restaurant exists
    restaurant = await crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if status:
        # Get orders filtered by status
        order_status = OrderStatus(status.value)
        orders = await crud.get_orders_by_status(db, order_status, skip=skip, limit=limit)
        # Filter by restaurant
        orders = [order for order in orders if order.restaurant_id == restaurant_id]
    else:
        orders = await crud.get_restaurant_orders(db, restaurant_id, skip=skip, limit=limit)
    
    return orders

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of orders to return"),
    status: Optional[OrderStatusEnum] = Query(None, description="Filter by order status"),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders with optional status filtering"""
    if status:
        order_status = OrderStatus(status.value)
        orders = await crud.get_orders_by_status(db, order_status, skip=skip, limit=limit)
    else:
        orders = await crud.get_orders(db, skip=skip, limit=limit)
    
    return orders