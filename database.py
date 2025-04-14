from beanie import Document, init_beanie, before_event
import motor.motor_asyncio
from models import User, Product, Order
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
    
    @property
    async def total_price(self) -> float:
        """Calculate total price of the order based on product prices."""
        total = 0.0
        for item in self.products:
            # Fetch the product by its ID
            product = await ProductDocument.get(item.product_id)
            if product:
                # Calculate the price for the item and update it
                total += product.price * item.quantity
        return total

    async def update_status(self, status: str):
        """Update order status."""
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
        await self.save()
    
    async def update_stock(self):
        """Update stock for each product in the order."""
        for item in self.products:
            product = await ProductDocument.get(item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for product: {product.name}")
        
            await product.update_stock(item.quantity)

async def init_db():
    """Initialize the database connection and Beanie ORM."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client["ecommerce"]  # Database name
    await init_beanie(database, document_models=[ProductDocument, UserDocument, OrderDocument])  # Initialize Beanie with the database and models
