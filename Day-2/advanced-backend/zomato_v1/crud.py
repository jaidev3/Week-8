from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models import Restaurant
from schemas import RestaurantCreate, RestaurantUpdate

async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate):
    """Create a new restaurant"""
    try:
        db_restaurant = Restaurant(**restaurant.dict())
        db.add(db_restaurant)
        await db.commit()
        await db.refresh(db_restaurant)
        return db_restaurant
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists") from exc

async def get_restaurant(db: AsyncSession, restaurant_id: int):
    """Get a restaurant by ID"""
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    return result.scalar_one_or_none()

async def get_restaurants(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all restaurants with pagination"""
    result = await db.execute(select(Restaurant).offset(skip).limit(limit))
    return result.scalars().all()

async def get_active_restaurants(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get only active restaurants"""
    result = await db.execute(
        select(Restaurant)
        .where(Restaurant.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def search_restaurants_by_cuisine(db: AsyncSession, cuisine_type: str, skip: int = 0, limit: int = 100):
    """Search restaurants by cuisine type"""
    result = await db.execute(
        select(Restaurant)
        .where(Restaurant.cuisine_type.ilike(f"%{cuisine_type}%"))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_restaurant(db: AsyncSession, restaurant_id: int, restaurant_update: RestaurantUpdate):
    """Update a restaurant"""
    try:
        result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        db_restaurant = result.scalar_one_or_none()
        if db_restaurant:
            update_data = restaurant_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_restaurant, field, value)
            await db.commit()
            await db.refresh(db_restaurant)
        return db_restaurant
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Restaurant with this name already exists") from exc

async def delete_restaurant(db: AsyncSession, restaurant_id: int):
    """Delete a restaurant"""
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    db_restaurant = result.scalar_one_or_none()
    if db_restaurant:
        await db.delete(db_restaurant)
        await db.commit()
    return db_restaurant

async def get_restaurant_by_name(db: AsyncSession, name: str):
    """Get restaurant by name (for duplicate checking)"""
    result = await db.execute(select(Restaurant).where(Restaurant.name == name))
    return result.scalar_one_or_none()
