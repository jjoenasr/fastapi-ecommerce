from beanie import Document, init_beanie, before_event
import motor.motor_asyncio
from models import User, Product, Order, OrderOut, OrderItemOut
from datetime import datetime, timezone
from fastapi import HTTPException

MONGO_URI = "mongodb://localhost:27017"  # MongoDB URI  

class UserDocument(Document, User):
    class Settings:
        collection = "users"  # MongoDB collection name

class ProductDocument(Document, Product):
    class Settings:
        collection = "products"  # MongoDB collection name
    
    async def update_stock(self, quantity: int):
        """Update stock when a product is purchased."""
        self.stock -= quantity
        self.updated_at = datetime.now(timezone.utc)
        await self.save()

# Beanie model for Order (database interaction)
class OrderDocument(Document, Order):
    class Settings:
        collection = "orders"  # MongoDB collection name

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
    
    async def get_detailed_order(self) -> OrderOut:
        """Display order details including product names and quantities."""
        order_items = []
        total_price = 0.0
        for item in self.items:
            product = await ProductDocument.get(item.product_id)
            if product:
                order_items.append(OrderItemOut(product=product, quantity=item.quantity))
                total_price += product.price * item.quantity
            else:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        return OrderOut(items=order_items, total_price=round(total_price, 2), status=self.status, created_at=self.created_at, updated_at=self.updated_at)

async def init_db():
    """Initialize the database connection and Beanie ORM."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client["ecommerce"]  # Database name
    await init_beanie(database, document_models=[ProductDocument, UserDocument, OrderDocument])  # Initialize Beanie with the database and models
