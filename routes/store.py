from fastapi import APIRouter, HTTPException, Path
from models import Product, OrderIn, OrderOut
from database import ProductDocument, OrderDocument
from routes.auth import user_depends
from typing import List, Annotated

router = APIRouter(prefix="/store", tags=["store"])

# Route to create a new product
@router.post("/products/", response_model=ProductDocument)
async def create_product(product: Product, current_user: user_depends):
    try:
        # Try to insert product into the database
        product_doc = ProductDocument(**product.model_dump())
        await product_doc.insert()  # Insert product into MongoDB
        return product
    except Exception as e:
        # Handle any unexpected errors during insert
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route to get all products in the catalog
@router.get("/products/", response_model=List[ProductDocument])
async def get_products():
    try:
        # Get products with positive stock
        products = await ProductDocument.find(ProductDocument.stock > 0).to_list()
        return products
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

# Route to get a specific product by ID
@router.get("/products/{product_id}", response_model=ProductDocument)
async def get_product(product_id: Annotated[str, Path(title="The ID of the product to retrieve")]):
    try:
        # Try to fetch the product by ID
        product = await ProductDocument.get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

# Route to create an order
@router.post("/orders/", response_model=OrderDocument)
async def create_order(order: OrderIn, current_user: user_depends):
    try:
        # Create a new OrderDocument
        order_doc = OrderDocument(**order.model_dump(), user_id=current_user.id)
        
        # Update stock before inserting order
        await order_doc.update_stock()
        
        # Insert the order into the database
        await order_doc.insert()
        return order_doc
    except Exception as e:
        # Handle any unexpected errors during order creation
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/my-orders", response_model=List[OrderOut])
async def get_orders(current_user: user_depends):
    try:
        orders = await OrderDocument.find(OrderDocument.user_id == current_user.id).to_list()
        if not orders:
            raise HTTPException(status_code=404, detail="No orders found for this user")
        # Convert orders to the response model
        orders_out = [await order.get_detailed_order() for order in orders]
        return orders_out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")
