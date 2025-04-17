from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, usually 'bearer'")

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

class ProductOut(BaseModel):
    id: Optional[int]
    name: str
    price: float 
    stock: int 
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] 

    class Config:
        from_attributes = True  # Enable ORM mode to read data as dict

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    product: ProductOut
    quantity: int

    class Config:
        from_attributes = True

class OrderIn(BaseModel):
    items: List[OrderItemIn]

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

