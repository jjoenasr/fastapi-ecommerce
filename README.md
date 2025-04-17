# FastAPI E-commerce API Implementations

This project contains two implementations of the same e-commerce API using FastAPI with different database backends:
- SQL implementation using SQLModel ORM
- MongoDB implementation using Beanie ODM

## Features

- User authentication with JWT
- Product management (CRUD operations)
- Order processing and tracking
- Stock management
- Pagination and filtering for product listing
- Error handling and logging

## Prerequisites

- Python 3.8+
- SQLite (for RDB version)
- MongoDB (for MongoDB version)
- pip package manager

## Installation & Setup

1. Clone the repository
2. Choose your preferred implementation:

### For SQL Implementation (ecommerce-rdb):
```sh
cd ecommerce-rdb
pip install -r requirements.txt
python seed.py  # Optional: populate with sample data
python main.py
```

### For MongoDB Implementation (ecommerce-mongodb):
```sh
cd ecommerce-mongodb
pip install -r requirements.txt
# Ensure MongoDB is running on localhost:27017
python main.py
```

## API Endpoints

Both implementations share the same API interface:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Store
- `POST /store/products/` - Create new product
- `GET /store/products/` - List all products
- `GET /store/products/{product_id}` - Get product details
- `GET /store/search` - Search products (RDB implementation only)
- `POST /store/orders/` - Create new order
- `GET /store/my-orders` - List user's orders

## Key Differences

### RDB Implementation (SQLModel)
- Uses SQLite as database
- Includes database seeding functionality
- Features advanced product search with price filtering
- Uses SQLModel for type-safe database operations

### MongoDB Implementation (Beanie)
- Uses MongoDB as database
- Leverages Beanie ODM for async operations
- Native support for document-based data model
- Simpler schema evolution

## Security Features

- Password hashing using bcrypt
- JWT token authentication
- Protected routes using OAuth2
- CORS middleware enabled

## Development

The API will be available at `http://localhost:8000` with interactive API documentation at `/docs`.

## Environment Variables

Common environment variables for both implementations:
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

Additional for MongoDB:
- `MONGO_URI` - MongoDB connection string (default: "mongodb://localhost:27017")