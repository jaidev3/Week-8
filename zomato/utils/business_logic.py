from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review
from typing import List, Optional
from decimal import Decimal

async def search_restaurants(
    db: AsyncSession,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    location: Optional[str] = None,
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100
):
    """Advanced restaurant search with multiple filters"""
    query = select(Restaurant).where(Restaurant.is_active == is_active)
    
    conditions = []
    
    if cuisine:
        conditions.append(Restaurant.cuisine_type.ilike(f"%{cuisine}%"))
    
    if min_rating is not None:
        conditions.append(Restaurant.rating >= min_rating)
    
    if location:
        conditions.append(Restaurant.address.ilike(f"%{location}%"))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Restaurant.rating.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_popular_menu_items(
    db: AsyncSession,
    restaurant_id: Optional[int] = None,
    limit: int = 10
):
    """Get most popular menu items based on order frequency"""
    query = select(
        MenuItem.id,
        MenuItem.name,
        MenuItem.restaurant_id,
        func.sum(OrderItem.quantity).label('total_ordered'),
        func.count(OrderItem.id).label('order_count')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)
    
    if restaurant_id:
        query = query.where(MenuItem.restaurant_id == restaurant_id)
    
    query = query.group_by(MenuItem.id, MenuItem.name, MenuItem.restaurant_id)\
                 .order_by(func.sum(OrderItem.quantity).desc())\
                 .limit(limit)
    
    result = await db.execute(query)
    return result.all()

async def calculate_estimated_delivery_time(
    db: AsyncSession,
    restaurant_id: int,
    menu_item_ids: List[int]
):
    """Calculate estimated delivery time based on preparation times"""
    # Get preparation times for all items
    result = await db.execute(
        select(MenuItem.preparation_time)
        .where(and_(
            MenuItem.id.in_(menu_item_ids),
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True
        ))
    )
    
    prep_times = [time for time in result.scalars().all() if time is not None]
    
    if not prep_times:
        return 30  # Default 30 minutes
    
    # Maximum prep time + 15 minutes for delivery
    max_prep_time = max(prep_times)
    return max_prep_time + 15

async def get_restaurant_revenue_by_period(
    db: AsyncSession,
    restaurant_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Calculate restaurant revenue for a specific period"""
    query = select(
        func.sum(Order.total_amount).label('total_revenue'),
        func.count(Order.id).label('total_orders'),
        func.avg(Order.total_amount).label('avg_order_value')
    ).where(Order.restaurant_id == restaurant_id)
    
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    
    result = await db.execute(query)
    return result.first()

async def get_customer_spending_by_period(
    db: AsyncSession,
    customer_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Calculate customer spending for a specific period"""
    query = select(
        func.sum(Order.total_amount).label('total_spent'),
        func.count(Order.id).label('total_orders'),
        func.avg(Order.total_amount).label('avg_order_value')
    ).where(Order.customer_id == customer_id)
    
    if start_date:
        query = query.where(Order.order_date >= start_date)
    if end_date:
        query = query.where(Order.order_date <= end_date)
    
    result = await db.execute(query)
    return result.first()

async def validate_order_items(
    db: AsyncSession,
    restaurant_id: int,
    items: List[dict]
):
    """Validate that all order items belong to the restaurant and are available"""
    menu_item_ids = [item['menu_item_id'] for item in items]
    
    # Check if all items exist and are available
    result = await db.execute(
        select(MenuItem.id, MenuItem.price, MenuItem.is_available)
        .where(and_(
            MenuItem.id.in_(menu_item_ids),
            MenuItem.restaurant_id == restaurant_id
        ))
    )
    
    available_items = {item.id: (item.price, item.is_available) for item in result.all()}
    
    errors = []
    for item in items:
        item_id = item['menu_item_id']
        if item_id not in available_items:
            errors.append(f"Menu item {item_id} not found in restaurant {restaurant_id}")
        elif not available_items[item_id][1]:  # is_available
            errors.append(f"Menu item {item_id} is not available")
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return available_items

async def calculate_order_total(
    available_items: dict,
    items: List[dict]
):
    """Calculate total order amount"""
    total = Decimal('0.00')
    
    for item in items:
        item_id = item['menu_item_id']
        quantity = item['quantity']
        price = available_items[item_id][0]  # price from validation
        total += price * quantity
    
    return total

async def get_trending_restaurants(
    db: AsyncSession,
    limit: int = 10,
    days: int = 7
):
    """Get trending restaurants based on recent order activity"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    result = await db.execute(
        select(
            Restaurant.id,
            Restaurant.name,
            Restaurant.cuisine_type,
            Restaurant.rating,
            func.count(Order.id).label('recent_orders'),
            func.sum(Order.total_amount).label('recent_revenue')
        )
        .join(Order, Restaurant.id == Order.restaurant_id)
        .where(Order.order_date >= cutoff_date)
        .group_by(Restaurant.id, Restaurant.name, Restaurant.cuisine_type, Restaurant.rating)
        .order_by(func.count(Order.id).desc())
        .limit(limit)
    )
    
    return result.all()

async def get_customer_recommendations(
    db: AsyncSession,
    customer_id: int,
    limit: int = 5
):
    """Get restaurant recommendations based on customer's order history"""
    # Get customer's favorite cuisines
    favorite_cuisines_result = await db.execute(
        select(Restaurant.cuisine_type)
        .join(Order, Restaurant.id == Order.restaurant_id)
        .where(Order.customer_id == customer_id)
        .group_by(Restaurant.cuisine_type)
        .order_by(func.count(Order.id).desc())
        .limit(3)
    )
    
    favorite_cuisines = [cuisine for cuisine in favorite_cuisines_result.scalars().all()]
    
    if not favorite_cuisines:
        # If no order history, recommend highly rated restaurants
        result = await db.execute(
            select(Restaurant)
            .where(and_(Restaurant.is_active == True, Restaurant.rating >= 4.0))
            .order_by(Restaurant.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    # Recommend restaurants with similar cuisines that customer hasn't ordered from
    ordered_restaurant_ids = await db.execute(
        select(Order.restaurant_id)
        .where(Order.customer_id == customer_id)
        .distinct()
    )
    ordered_ids = [id for id in ordered_restaurant_ids.scalars().all()]
    
    conditions = [
        Restaurant.is_active == True,
        Restaurant.cuisine_type.in_(favorite_cuisines),
        Restaurant.rating >= 3.5
    ]
    
    if ordered_ids:
        conditions.append(Restaurant.id.notin_(ordered_ids))
    
    result = await db.execute(
        select(Restaurant)
        .where(and_(*conditions))
        .order_by(Restaurant.rating.desc())
        .limit(limit)
    )
    
    return result.scalars().all()