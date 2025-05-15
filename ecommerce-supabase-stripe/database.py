from sqlmodel import Field, Session, String, SQLModel, create_engine, Relationship, select, Column, func, DateTime
from pydantic import EmailStr
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from config import settings

db_url = f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:5432/postgres'

engine = create_engine(db_url, future=True)

class User(SQLModel, table=True):
    id: UUID = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), nullable=False))
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))

    orders: list["Order"] = Relationship(back_populates="user")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    price: float
    stock: int = 10 # Default stock to 10
    description: Optional[str] = None
    image: Optional[str] = None
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), nullable=False))
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    order_items: list["OrderItem"] = Relationship(back_populates="product", cascade_delete=True)

    def update_stock(self, quantity: int, db: Session):
        if self.stock >= quantity:
            self.stock -= quantity
            db.add(self)  # Add the updated product to the session
            db.commit()  # Commit the changes to the database
            db.refresh(self)  # Refresh the instance to get the updated data
        else:
            raise ValueError("Not enough stock available")
    
    @property
    def imageURL(self) -> str:
        if self.image:
            return f"{settings.supabase_bucket_url}/{self.image}"
        return f"{settings.supabase_bucket_url}/default.png"
    

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id",  ondelete="CASCADE")
    quantity: int
    order_id: int = Field(foreign_key="order.id",  ondelete="CASCADE")
    
    order: "Order" = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="user.id", nullable=True, ondelete="SET NULL")
    status: Literal["Pending", "Paid", "Shipped", "Delivered"] = Field(sa_type=String, default="Pending")
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), nullable=False))
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()))
    stripe_session_id: Optional[str] = None  # Optional field for Stripe session ID
    user: User = Relationship(back_populates="orders")
    items: list[OrderItem] = Relationship(back_populates="order", cascade_delete=True)

    @property
    def total_price(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items if item.product)

    def update_status(self, new_status: str, db: Session):
        if new_status in ["Pending", "Paid", "Shipped", "Delivered"]:
            self.status = new_status
            db.add(self)
            db.commit()
            db.refresh(self)
        else:
            raise ValueError("Invalid status value")
    
    def update_stock(self, db: Session):
        for item in self.items:
            product = db.exec(select(Product).where(Product.id == item.product_id)).first()
            if product:
                product.update_stock(item.quantity, db)
            else:
                raise ValueError("Product not found in order items")


def create_tables():
    SQLModel.metadata.create_all(engine)
    SQLModel.model_rebuild() # Rebuild the model to ensure all relationships are set up correctly

def get_session():
    with Session(engine) as session:
        yield session
