from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, time
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
