from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from models import Restaurant, MenuItem
from schemas import RestaurantCreate, RestaurantUpdate, MenuItemCreate, MenuItemUpdate

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

async def get_restaurant_with_menu(db: AsyncSession, restaurant_id: int):
    """Get restaurant with all its menu items"""
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.menu_items))
        .where(Restaurant.id == restaurant_id)
    )
    return result.scalar_one_or_none()

# MenuItem CRUD Operations
async def create_menu_item(db: AsyncSession, menu_item: MenuItemCreate):
    """Create a new menu item"""
    try:
        # Check if restaurant exists
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == menu_item.restaurant_id))
        if not restaurant_result.scalar_one_or_none():
            raise ValueError("Restaurant not found")
        
        db_menu_item = MenuItem(**menu_item.dict())
        db.add(db_menu_item)
        await db.commit()
        await db.refresh(db_menu_item)
        return db_menu_item
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Failed to create menu item") from exc

async def get_menu_item(db: AsyncSession, item_id: int):
    """Get a menu item by ID"""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    return result.scalar_one_or_none()

async def get_menu_item_with_restaurant(db: AsyncSession, item_id: int):
    """Get menu item with restaurant details"""
    result = await db.execute(
        select(MenuItem)
        .options(selectinload(MenuItem.restaurant))
        .where(MenuItem.id == item_id)
    )
    return result.scalar_one_or_none()

async def get_menu_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all menu items with pagination"""
    result = await db.execute(select(MenuItem).offset(skip).limit(limit))
    return result.scalars().all()

async def get_restaurant_menu_items(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 100):
    """Get all menu items for a specific restaurant"""
    result = await db.execute(
        select(MenuItem)
        .where(MenuItem.restaurant_id == restaurant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def search_menu_items(db: AsyncSession, category: str = None, vegetarian: bool = None, vegan: bool = None, available: bool = None, skip: int = 0, limit: int = 100):
    """Search menu items by various filters"""
    query = select(MenuItem)
    
    conditions = []
    if category:
        conditions.append(MenuItem.category.ilike(f"%{category}%"))
    if vegetarian is not None:
        conditions.append(MenuItem.is_vegetarian == vegetarian)
    if vegan is not None:
        conditions.append(MenuItem.is_vegan == vegan)
    if available is not None:
        conditions.append(MenuItem.is_available == available)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_menu_item(db: AsyncSession, item_id: int, menu_item_update: MenuItemUpdate):
    """Update a menu item"""
    try:
        result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
        db_menu_item = result.scalar_one_or_none()
        if db_menu_item:
            update_data = menu_item_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_menu_item, field, value)
            await db.commit()
            await db.refresh(db_menu_item)
        return db_menu_item
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Failed to update menu item") from exc

async def delete_menu_item(db: AsyncSession, item_id: int):
    """Delete a menu item"""
    result = await db.execute(select(MenuItem).where(MenuItem.id == item_id))
    db_menu_item = result.scalar_one_or_none()
    if db_menu_item:
        await db.delete(db_menu_item)
        await db.commit()
    return db_menu_item

async def get_average_menu_price(db: AsyncSession, restaurant_id: int):
    """Calculate average menu price for a restaurant"""
    from sqlalchemy import func
    result = await db.execute(
        select(func.avg(MenuItem.price))
        .where(MenuItem.restaurant_id == restaurant_id)
    )
    avg_price = result.scalar()
    return float(avg_price) if avg_price else 0.0
