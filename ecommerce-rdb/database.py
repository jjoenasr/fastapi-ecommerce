from sqlmodel import Field, Session, String, SQLModel, create_engine, Relationship, select
from pydantic import EmailStr
from datetime import datetime, timezone
from typing import Optional, Literal

sqlite_file_name = "ecommerce.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Default to current UTC time

    orders: list["Order"] = Relationship(back_populates="user")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    price: float
    stock: int = 10 # Default stock to 10
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Default to current UTC time
    updated_at: Optional[datetime] = None  # Updated time can be None initially
    order_items: list["OrderItem"] = Relationship(back_populates="product")

    def update_stock(self, quantity: int, db: Session):
        if self.stock >= quantity:
            self.stock -= quantity
            self.updated_at = datetime.now(timezone.utc)  # Update the timestamp
            db.add(self)  # Add the updated product to the session
            db.commit()  # Commit the changes to the database
            db.refresh(self)  # Refresh the instance to get the updated data
        else:
            raise ValueError("Not enough stock available")
    


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    order_id: int = Field(foreign_key="order.id")
    
    order: "Order" = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: Literal["Pending", "Shipped", "Delivered"] = Field(sa_type=String, default="Pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    user: User = Relationship(back_populates="orders")
    items: list[OrderItem] = Relationship(back_populates="order")

    @property
    def total_price(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items if item.product)

    def update_status(self, new_status: str, db: Session):
        if new_status in ["Pending", "Shipped", "Delivered"]:
            self.status = new_status
            self.updated_at = datetime.now(timezone.utc)
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
