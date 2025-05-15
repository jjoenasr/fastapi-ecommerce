from fastapi import APIRouter, HTTPException, Path, Query, Depends, Form, UploadFile, File
from schemas import ProductOut, OrderIn, OrderOut
from database import Product, Order, OrderItem, get_session
from routes.auth import user_depends
from sqlmodel import Session, select, desc
from typing import List, Annotated, Optional, Literal
from utils import save_image

router = APIRouter(prefix="/store", tags=["store"])

# Route to create a new product
@router.post("/products/", response_model=ProductOut)
def create_product(current_user: user_depends,
                   name: Annotated[str, Form()],
                   price: Annotated[float, Form(gt=0)],
                   stock: Annotated[Optional[int], Form(ge=0)] = 10,
                   description: Annotated[Optional[str], Form()] = None,
                   image: Optional[UploadFile] = File(None),
                   db: Session = Depends(get_session)):
    try:
        image_url = None
        if image:
            image_url = save_image(image)  # Save the image to the server
        product_doc = Product(name=name, price=price, description=description, stock=stock, image_url=image_url)
        db.add(product_doc)
        db.commit()
        db.refresh(product_doc)  # Refresh the instance to get the updated data
        return product_doc
    except Exception as e:
        # Handle any unexpected errors during insert
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route to get all products in the catalog
@router.get("/products/", response_model=List[ProductOut])
def get_products(offset: Annotated[int, Query(ge=0)] = 0,
                limit: Annotated[int, Query(gt=0)] = 10,
                order_by: Literal["name", "-name", "created_at", "-created_at"] = "name",
                db: Session = Depends(get_session)):
    # Define the mapping for order_by parameter
    order_map = {
        "name": Product.name,
        "-name": desc(Product.name),
        "created_at": Product.created_at,
        "-created_at": desc(Product.created_at)
    }
    try:
        products = db.exec(select(Product).where(Product.stock > 0).order_by(order_map.get(order_by)).offset(offset).limit(limit)).all()
        return products
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

# Route to get a specific product by ID
@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: Annotated[str, Path(title="The ID of the product to retrieve")], db: Session = Depends(get_session)):
    try:
        # Try to fetch the product by ID
        product = db.exec(select(Product).where(Product.id == product_id)).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

# Route to search for products
@router.get("/search", response_model=List[ProductOut])
def search_products(query: Annotated[Optional[str], Query(max_length=50)] = None,
                    min_price: Annotated[Optional[float], Query(ge=0)] = None,
                    max_price: Annotated[Optional[float], Query(gt=0)] = None,
                    db: Session = Depends(get_session)):
    try:
        statement = select(Product).where(Product.stock > 0)
        if query:
            statement = statement.where(Product.name.ilike(f"%{query}%"))
        if min_price is not None:
            statement = statement.where(Product.price >= min_price)
        if max_price is not None:
            statement = statement.where(Product.price <= max_price)
        products = db.exec(statement.order_by(Product.name)).all()
        return products
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

# Route to create an order
@router.post("/orders/", response_model=OrderOut)
def create_order(order: OrderIn, current_user: user_depends, db: Session = Depends(get_session)):
    try:
        # Step 1: Create a new Order object
        order_doc = Order(user_id=current_user.id)
        
        # Step 2: Create the OrderItems and append to the Order
        for item in order.items:
            order_item = OrderItem(product_id=item.product_id, quantity=item.quantity)
            order_doc.items.append(order_item)

        # Step 3: Update the stock before inserting the order
        order_doc.update_stock(db)  # This will reduce the stock based on the quantities
        
        # Step 4: Insert the order into the database
        db.add(order_doc)
        db.commit()
        db.refresh(order_doc)  # Refresh the instance to get the updated data
        return order_doc
    except Exception as e:
        # Handle any unexpected errors during order creation
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/my-orders", response_model=List[OrderOut])
def get_orders(current_user: user_depends, db: Session = Depends(get_session)):
    try:
        orders = db.exec(select(Order).where(Order.user_id == current_user.id)).all()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")
