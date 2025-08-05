from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal
import re

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

# Nested Schemas for complex responses
class MenuItemWithRestaurant(MenuItemResponse):
    restaurant: RestaurantResponse

class RestaurantWithMenu(RestaurantResponse):
    menu_items: List[MenuItemResponse] = []
