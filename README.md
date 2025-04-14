# FastAPI E-commerce API

A RESTful API built with FastAPI and MongoDB (via Beanie ODM) for a basic e-commerce platform.

## Features

- User authentication with JWT
- Product management
- Order processing
- Stock management
- MongoDB integration using Beanie ODM

## Prerequisites

- Python 3.8+
- MongoDB running locally
- pip package manager

## Installation

1. Clone the repository
2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Ensure MongoDB is running on localhost:27017

## Running the Application

Start the server with:

```sh
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Store
- `POST /store/products/` - Create new product
- `GET /store/products/` - List all products
- `GET /store/products/{product_id}` - Get product details
- `POST /store/orders/` - Create new order
- `GET /store/my-orders` - List user's orders

## Project Structure

```
├── main.py           # Application entry point
├── database.py       # Database models and configuration
├── models.py         # Pydantic models
├── utils.py          # Utility functions
├── requirements.txt  # Project dependencies
└── routes/          
    ├── auth.py      # Authentication routes
    └── store.py     # Store management routes
```

## Security

- Password hashing using bcrypt
- JWT token authentication
- Protected routes using OAuth2

## Environment Variables

The following environment variables can be configured:
- `MONGO_URI` - MongoDB connection string (default: "mongodb://localhost:27017")
- `SECRET_KEY` - JWT secret key