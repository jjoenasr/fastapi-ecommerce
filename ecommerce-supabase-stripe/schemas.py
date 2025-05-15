from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token for obtaining new access tokens")
    token_type: Literal["bearer"] = Field("bearer", description="Type of the token")

class UserIn(BaseModel):
    username: str
    email: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

class ProductIn(BaseModel):
    name: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: Optional[int] = Field(default=10, ge=0, description="Stock must be greater than or equal to 0")
    description: Optional[str] = None

    class Config:
        from_attributes = True  # Enable ORM mode to read data as dict

class ProductOut(BaseModel):
    id: int
    name: str
    price: float 
    stock: int 
    description: Optional[str]
    imageURL: Optional[str]
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
    status: Literal["Pending", "Paid", "Shipped", "Delivered"]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        
class ChatRequest(BaseModel):
    prompt: str
