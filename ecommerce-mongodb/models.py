from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId
from typing import List, Optional, Literal
from datetime import datetime, timezone

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, usually 'bearer'")

class User(BaseModel):
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Default to current UTC time

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    username: str
    email: str
    created_at: datetime

class ProductIn(BaseModel):
    name: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: Optional[int] = Field(default=10, ge=0, description="Stock must be greater than or equal to 0")
    description: Optional[str]

    class Config:
        from_attributes = True  # Enable ORM mode to read data as dict


class Product(BaseModel):
    name: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: int = 10 # Default stock to 10
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Default to current UTC time
    updated_at: Optional[datetime] = None  # Updated time can be None initially

    class Config:
        from_attributes = True  # Enable ORM mode to read data as dict

class OrderItem(BaseModel):
    product_id: PydanticObjectId  # MongoDB ObjectId for product reference
    quantity: int

    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    product: Product
    quantity: int

    class Config:
        from_attributes = True

class Order(BaseModel):
    user_id: PydanticObjectId
    items: List[OrderItem]
    status: Literal["Pending", "Shipped", "Delivered"] = "Pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderIn(BaseModel):
    items: List[OrderItem]

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    items: List[OrderItemOut]
    total_price: float
    status: Literal["Pending", "Shipped", "Delivered"]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

