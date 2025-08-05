from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal
from enum import Enum
import re

class OrderStatusEnum(str, Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: str = Field(..., min_length=1, max_length=50)
    address: str = Field(..., min_length=5)
    phone_number: str = Field(..., min_length=10, max_length=20)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    opening_time: time
    closing_time: time
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10:
            raise ValueError('Phone number must contain at least 10 digits')
        return v
    
    @validator('closing_time')
    def validate_times(cls, v, values):
        if 'opening_time' in values and v <= values['opening_time']:
            raise ValueError('Closing time must be after opening time')
        return v

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=5)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError('Phone number must contain at least 10 digits')
        return v

class RestaurantResponse(RestaurantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# MenuItem Schemas
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=50)
    is_vegetarian: bool = Field(default=False)
    is_vegan: bool = Field(default=False)
    is_available: bool = Field(default=True)
    preparation_time: Optional[int] = Field(None, ge=1, le=300)  # 1-300 minutes
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('is_vegan')
    def validate_vegan_vegetarian(cls, v, values):
        if v and not values.get('is_vegetarian', False):
            raise ValueError('Vegan items must also be vegetarian')
        return v

class MenuItemCreate(MenuItemBase):
    restaurant_id: int = Field(..., gt=0)

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, ge=1, le=300)
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('is_vegan')
    def validate_vegan_vegetarian(cls, v, values):
        if v is not None and v and not values.get('is_vegetarian', False):
            raise ValueError('Vegan items must also be vegetarian')
        return v

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Customer Schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone_number: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5)
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10:
            raise ValueError('Phone number must contain at least 10 digits')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = Field(None, min_length=5)
    is_active: Optional[bool] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError('Phone number must contain at least 10 digits')
        return v

class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)
    special_requests: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    item_price: Decimal

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    restaurant_id: int = Field(..., gt=0)
    delivery_address: str = Field(..., min_length=5)
    special_instructions: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1)

class OrderUpdate(BaseModel):
    order_status: Optional[OrderStatusEnum] = None
    delivery_address: Optional[str] = Field(None, min_length=5)
    special_instructions: Optional[str] = None
    delivery_time: Optional[datetime] = None

class OrderResponse(OrderBase):
    id: int
    customer_id: int
    order_status: OrderStatusEnum
    total_amount: Decimal
    order_date: datetime
    delivery_time: Optional[datetime]

    class Config:
        from_attributes = True

# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    customer_id: int
    restaurant_id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Complex nested schemas for detailed responses
class MenuItemWithRestaurant(MenuItemResponse):
    restaurant: RestaurantResponse

class RestaurantWithMenu(RestaurantResponse):
    menu_items: List[MenuItemResponse] = []

class OrderItemWithMenuItem(OrderItemResponse):
    menu_item: MenuItemResponse

class OrderWithDetails(OrderResponse):
    customer: CustomerResponse
    restaurant: RestaurantResponse
    order_items: List[OrderItemWithMenuItem] = []

class CustomerWithOrders(CustomerResponse):
    orders: List[OrderResponse] = []

class RestaurantWithReviews(RestaurantResponse):
    reviews: List[ReviewResponse] = []
    average_rating: Optional[float] = None

# Analytics Schemas
class RestaurantAnalytics(BaseModel):
    restaurant_id: int
    total_orders: int
    total_revenue: Decimal
    average_order_value: Decimal
    average_rating: float
    total_reviews: int
    popular_items: List[dict]
    orders_by_status: dict

class CustomerAnalytics(BaseModel):
    customer_id: int
    total_orders: int
    total_spent: Decimal
    average_order_value: Decimal
    favorite_restaurants: List[dict]
    favorite_cuisines: List[dict]
    orders_by_status: dict
