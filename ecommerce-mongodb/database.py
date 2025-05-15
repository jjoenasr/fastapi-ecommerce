from beanie import Document, init_beanie, PydanticObjectId
from pydantic import Field, EmailStr
from typing import Optional, List, Literal
import motor.motor_asyncio
from schemas import OrderItemOut, OrderItem, OrderOut
from datetime import datetime, timezone
from fastapi import HTTPException

MONGO_URI = "mongodb://localhost:27017"  # MongoDB URI  

class UserDocument(Document):
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        collection = "users"  # MongoDB collection name

class ProductDocument(Document):
    name: str = Field(max_length=100, index=True)
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    stock: int = 10 # Default stock to 10
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Default to current UTC time
    updated_at: Optional[datetime] = None  # Updated time can be None initially

    class Settings:
        collection = "products"  # MongoDB collection name
    
    async def update_stock(self, quantity: int):
        """Update stock when a product is purchased."""
        self.stock -= quantity
        self.updated_at = datetime.now(timezone.utc)
        await self.save()


# Beanie model for Order (database interaction)
class OrderDocument(Document):
    user_id: PydanticObjectId
    items: List[OrderItem]
    status: Literal["Pending", "Shipped", "Delivered"] = "Pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Settings:
        collection = "orders"  # MongoDB collection name
    
    @property
    async def total_price(self) -> float:
        """Calculate total price of the order."""
        total = 0.0
        for item in self.items:
            product = await ProductDocument.get(item.product_id)
            if product:
                total += product.price * item.quantity
            else:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        return round(total, 2)
    
    @property
    async def items_list(self) -> List[OrderItemOut]:
        """Get full item list with product details."""
        items = []
        for item in self.items:
            product = await ProductDocument.get(item.product_id)
            if product:
                items.append(OrderItemOut(product=product, quantity=item.quantity))
            else:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        return items

    async def update_status(self, status: str):
        """Update order status."""
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
        await self.save()
    
    async def update_stock(self):
        """Update stock for each product in the order."""
        for item in self.items:
            product = await ProductDocument.get(item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product: {product.name}")
        
            await product.update_stock(item.quantity)
    
    async def get_order_out(self) -> OrderOut:
        """Convert OrderDocument to OrderOut."""
        total_price = await self.total_price
        items_list = await self.items_list
        return OrderOut(
            id=self.id,
            items_list=items_list,
            total_price=total_price,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

async def init_db():
    """Initialize the database connection and Beanie ORM."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client["ecommerce"]  # Database name
    await init_beanie(database, document_models=[ProductDocument, UserDocument, OrderDocument])  # Initialize Beanie with the database and models
