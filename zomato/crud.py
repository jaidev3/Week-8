from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from models import Restaurant, MenuItem, Customer, Order, OrderItem, Review, OrderStatus
from schemas import (
    RestaurantCreate, RestaurantUpdate, MenuItemCreate, MenuItemUpdate,
    CustomerCreate, CustomerUpdate, OrderCreate, OrderUpdate, ReviewCreate
)
from decimal import Decimal

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
    result = await db.execute(
        select(func.avg(MenuItem.price))
        .where(MenuItem.restaurant_id == restaurant_id)
    )
    avg_price = result.scalar()
    return float(avg_price) if avg_price else 0.0

# Customer CRUD Operations
async def create_customer(db: AsyncSession, customer: CustomerCreate):
    """Create a new customer"""
    try:
        db_customer = Customer(**customer.dict())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Customer with this email already exists") from exc

async def get_customer(db: AsyncSession, customer_id: int):
    """Get a customer by ID"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalar_one_or_none()

async def get_customer_by_email(db: AsyncSession, email: str):
    """Get customer by email"""
    result = await db.execute(select(Customer).where(Customer.email == email))
    return result.scalar_one_or_none()

async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all customers with pagination"""
    result = await db.execute(select(Customer).offset(skip).limit(limit))
    return result.scalars().all()

async def update_customer(db: AsyncSession, customer_id: int, customer_update: CustomerUpdate):
    """Update a customer"""
    try:
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        db_customer = result.scalar_one_or_none()
        if db_customer:
            update_data = customer_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_customer, field, value)
            await db.commit()
            await db.refresh(db_customer)
        return db_customer
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Customer with this email already exists") from exc

async def delete_customer(db: AsyncSession, customer_id: int):
    """Delete a customer"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    db_customer = result.scalar_one_or_none()
    if db_customer:
        await db.delete(db_customer)
        await db.commit()
    return db_customer

# Order CRUD Operations
async def create_order(db: AsyncSession, customer_id: int, order: OrderCreate):
    """Create a new order with order items"""
    try:
        # Verify customer exists
        customer_result = await db.execute(select(Customer).where(Customer.id == customer_id))
        if not customer_result.scalar_one_or_none():
            raise ValueError("Customer not found")
        
        # Verify restaurant exists
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == order.restaurant_id))
        if not restaurant_result.scalar_one_or_none():
            raise ValueError("Restaurant not found")
        
        # Calculate total amount
        total_amount = Decimal('0.00')
        order_items_data = []
        
        for item in order.items:
            # Get menu item and verify it exists and is available
            menu_item_result = await db.execute(
                select(MenuItem).where(
                    and_(
                        MenuItem.id == item.menu_item_id,
                        MenuItem.restaurant_id == order.restaurant_id,
                        MenuItem.is_available == True
                    )
                )
            )
            menu_item = menu_item_result.scalar_one_or_none()
            if not menu_item:
                raise ValueError(f"Menu item {item.menu_item_id} not found or not available")
            
            item_total = menu_item.price * item.quantity
            total_amount += item_total
            
            order_items_data.append({
                'menu_item_id': item.menu_item_id,
                'quantity': item.quantity,
                'item_price': menu_item.price,
                'special_requests': item.special_requests
            })
        
        # Create order
        db_order = Order(
            customer_id=customer_id,
            restaurant_id=order.restaurant_id,
            total_amount=total_amount,
            delivery_address=order.delivery_address,
            special_instructions=order.special_instructions,
            order_status=OrderStatus.PLACED
        )
        db.add(db_order)
        await db.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items_data:
            db_order_item = OrderItem(order_id=db_order.id, **item_data)
            db.add(db_order_item)
        
        await db.commit()
        await db.refresh(db_order)
        return db_order
        
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Failed to create order") from exc

async def get_order(db: AsyncSession, order_id: int):
    """Get an order by ID with full details"""
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.restaurant),
            selectinload(Order.order_items).selectinload(OrderItem.menu_item)
        )
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all orders with pagination"""
    result = await db.execute(select(Order).offset(skip).limit(limit))
    return result.scalars().all()

async def get_customer_orders(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 100):
    """Get all orders for a specific customer"""
    result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(desc(Order.order_date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_restaurant_orders(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 100):
    """Get all orders for a specific restaurant"""
    result = await db.execute(
        select(Order)
        .where(Order.restaurant_id == restaurant_id)
        .order_by(desc(Order.order_date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_order_status(db: AsyncSession, order_id: int, order_update: OrderUpdate):
    """Update order status and other fields"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    db_order = result.scalar_one_or_none()
    if db_order:
        update_data = order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        await db.commit()
        await db.refresh(db_order)
    return db_order

async def get_orders_by_status(db: AsyncSession, status: OrderStatus, skip: int = 0, limit: int = 100):
    """Get orders by status"""
    result = await db.execute(
        select(Order)
        .where(Order.order_status == status)
        .order_by(desc(Order.order_date))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# Review CRUD Operations
async def create_review(db: AsyncSession, customer_id: int, order_id: int, review: ReviewCreate):
    """Create a review for a completed order"""
    try:
        # Verify order exists and belongs to customer
        order_result = await db.execute(
            select(Order).where(
                and_(
                    Order.id == order_id,
                    Order.customer_id == customer_id,
                    Order.order_status == OrderStatus.DELIVERED
                )
            )
        )
        db_order = order_result.scalar_one_or_none()
        if not db_order:
            raise ValueError("Order not found, doesn't belong to customer, or not completed")
        
        # Check if review already exists
        existing_review = await db.execute(
            select(Review).where(
                and_(
                    Review.order_id == order_id,
                    Review.customer_id == customer_id
                )
            )
        )
        if existing_review.scalar_one_or_none():
            raise ValueError("Review already exists for this order")
        
        # Create review
        db_review = Review(
            customer_id=customer_id,
            restaurant_id=db_order.restaurant_id,
            order_id=order_id,
            rating=review.rating,
            comment=review.comment
        )
        db.add(db_review)
        await db.commit()
        await db.refresh(db_review)
        
        # Update restaurant average rating
        await update_restaurant_rating(db, db_order.restaurant_id)
        
        return db_review
        
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError("Failed to create review") from exc

async def get_restaurant_reviews(db: AsyncSession, restaurant_id: int, skip: int = 0, limit: int = 100):
    """Get all reviews for a restaurant"""
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.customer))
        .where(Review.restaurant_id == restaurant_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_customer_reviews(db: AsyncSession, customer_id: int, skip: int = 0, limit: int = 100):
    """Get all reviews by a customer"""
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.restaurant))
        .where(Review.customer_id == customer_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_restaurant_rating(db: AsyncSession, restaurant_id: int):
    """Update restaurant's average rating based on reviews"""
    result = await db.execute(
        select(func.avg(Review.rating))
        .where(Review.restaurant_id == restaurant_id)
    )
    avg_rating = result.scalar()
    
    if avg_rating:
        restaurant_result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        restaurant = restaurant_result.scalar_one_or_none()
        if restaurant:
            restaurant.rating = float(avg_rating)
            await db.commit()

# Analytics Functions
async def get_restaurant_analytics(db: AsyncSession, restaurant_id: int):
    """Get comprehensive analytics for a restaurant"""
    # Total orders and revenue
    orders_result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
        .where(Order.restaurant_id == restaurant_id)
    )
    total_orders, total_revenue = orders_result.first()
    total_orders = total_orders or 0
    total_revenue = total_revenue or Decimal('0.00')
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
    
    # Reviews and rating
    reviews_result = await db.execute(
        select(func.count(Review.id), func.avg(Review.rating))
        .where(Review.restaurant_id == restaurant_id)
    )
    total_reviews, avg_rating = reviews_result.first()
    total_reviews = total_reviews or 0
    avg_rating = float(avg_rating) if avg_rating else 0.0
    
    # Orders by status
    status_result = await db.execute(
        select(Order.order_status, func.count(Order.id))
        .where(Order.restaurant_id == restaurant_id)
        .group_by(Order.order_status)
    )
    orders_by_status = {status.value: count for status, count in status_result.all()}
    
    # Popular items
    popular_items_result = await db.execute(
        select(
            MenuItem.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.quantity * OrderItem.item_price).label('total_revenue')
        )
        .join(OrderItem, MenuItem.id == OrderItem.menu_item_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.restaurant_id == restaurant_id)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(desc('total_quantity'))
        .limit(10)
    )
    popular_items = [
        {
            'name': name,
            'total_quantity': int(quantity),
            'total_revenue': float(revenue)
        }
        for name, quantity, revenue in popular_items_result.all()
    ]
    
    return {
        'restaurant_id': restaurant_id,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'average_rating': avg_rating,
        'total_reviews': total_reviews,
        'popular_items': popular_items,
        'orders_by_status': orders_by_status
    }

async def get_customer_analytics(db: AsyncSession, customer_id: int):
    """Get comprehensive analytics for a customer"""
    # Total orders and spending
    orders_result = await db.execute(
        select(func.count(Order.id), func.sum(Order.total_amount))
        .where(Order.customer_id == customer_id)
    )
    total_orders, total_spent = orders_result.first()
    total_orders = total_orders or 0
    total_spent = total_spent or Decimal('0.00')
    
    # Average order value
    avg_order_value = total_spent / total_orders if total_orders > 0 else Decimal('0.00')
    
    # Orders by status
    status_result = await db.execute(
        select(Order.order_status, func.count(Order.id))
        .where(Order.customer_id == customer_id)
        .group_by(Order.order_status)
    )
    orders_by_status = {status.value: count for status, count in status_result.all()}
    
    # Favorite restaurants
    favorite_restaurants_result = await db.execute(
        select(
            Restaurant.name,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_spent')
        )
        .join(Order, Restaurant.id == Order.restaurant_id)
        .where(Order.customer_id == customer_id)
        .group_by(Restaurant.id, Restaurant.name)
        .order_by(desc('order_count'))
        .limit(5)
    )
    favorite_restaurants = [
        {
            'name': name,
            'order_count': int(count),
            'total_spent': float(spent)
        }
        for name, count, spent in favorite_restaurants_result.all()
    ]
    
    # Favorite cuisines
    favorite_cuisines_result = await db.execute(
        select(
            Restaurant.cuisine_type,
            func.count(Order.id).label('order_count')
        )
        .join(Order, Restaurant.id == Order.restaurant_id)
        .where(Order.customer_id == customer_id)
        .group_by(Restaurant.cuisine_type)
        .order_by(desc('order_count'))
        .limit(5)
    )
    favorite_cuisines = [
        {
            'cuisine_type': cuisine,
            'order_count': int(count)
        }
        for cuisine, count in favorite_cuisines_result.all()
    ]
    
    return {
        'customer_id': customer_id,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'average_order_value': avg_order_value,
        'favorite_restaurants': favorite_restaurants,
        'favorite_cuisines': favorite_cuisines,
        'orders_by_status': orders_by_status
    }
