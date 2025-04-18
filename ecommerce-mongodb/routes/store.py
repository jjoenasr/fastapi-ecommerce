from fastapi import APIRouter, HTTPException, Path, Query, Form, UploadFile, File
from models import ProductOut, OrderIn, OrderOut
from database import ProductDocument, OrderDocument
from routes.auth import user_depends
from typing import List, Annotated, Literal, Optional
from utils import save_image

router = APIRouter(prefix="/store", tags=["store"])

# Route to create a new product
@router.post("/products/", response_model=ProductOut)
async def create_product(current_user: user_depends,
                        name: Annotated[str, Form()],
                        price: Annotated[float, Form(gt=0)],
                        stock: Annotated[Optional[int], Form(ge=0)] = 10,
                        description: Annotated[Optional[str], Form()] = None,
                        image: Optional[UploadFile] = File(None)):
    try:
        image_url = None
        if image:
            image_url = save_image(image)  # Save the image to the server
        product_doc = ProductDocument(name=name, price=price, description=description, stock=stock, image_url=image_url)
        await product_doc.insert()  # Insert product into MongoDB
        return product_doc
    except Exception as e:
        # Handle any unexpected errors during insert
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route to get all products in the catalog
@router.get("/products/", response_model=List[ProductOut])
async def get_products(offset: Annotated[int, Query(ge=0)] = 0,
                limit: Annotated[int, Query(gt=0)] = 10,
                order_by: Literal["name", "-name", "created_at", "-created_at"] = "name"):
    try:
        # Map order_by string to Beanie field sort
        sort_field = order_by.lstrip("-")
        sort_direction = -1 if order_by.startswith("-") else 1
        # Get products with positive stock
        products = await ProductDocument.find(ProductDocument.stock > 0).sort((sort_field, sort_direction)).skip(offset).limit(limit).to_list()
        return products
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

# Route to get a specific product by ID
@router.get("/products/{product_id}", response_model=ProductOut)
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

# Route to search products by name or price range
@router.get("/search", response_model=List[ProductOut])
async def search_products(query: Annotated[Optional[str], Query(max_length=50)] = None,
                    min_price: Annotated[Optional[float], Query(ge=0)] = None,
                    max_price: Annotated[Optional[float], Query(gt=0)] = None):
    try:
        # Build the search query based on provided parameters
        search_query = {}
        if query:
            search_query["name"] = {"$regex": query, "$options": "i"}
        if min_price is not None:
            search_query["price"] = {"$gte": min_price}
        if max_price is not None:
            search_query["price"] = {"$lte": max_price}

        # Fetch products matching the search criteria
        products = await ProductDocument.find(ProductDocument.stock > 0).find(search_query).to_list()
        return products
    except Exception as e:
        # Handle any unexpected errors during query
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


# Route to create an order
@router.post("/orders/", response_model=OrderOut)
async def create_order(order: OrderIn, current_user: user_depends):
    try:
        # Create a new OrderDocument
        order_doc = OrderDocument(**order.model_dump(), user_id=current_user.id)
        
        # Update stock before inserting order
        await order_doc.update_stock()
        
        # Insert the order into the database
        await order_doc.insert()
        order_out = await order_doc.get_order_out()
        return order_out
    except Exception as e:
        # Handle any unexpected errors during order creation
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/my-orders", response_model=List[OrderOut])
async def get_orders(current_user: user_depends):
    try:
        orders = await OrderDocument.find(OrderDocument.user_id == current_user.id).to_list()
        orders_out = [await order.get_order_out() for order in orders]
        return orders_out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")
