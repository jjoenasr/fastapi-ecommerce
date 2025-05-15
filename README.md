# FastAPI E-commerce API Implementations

This project contains three implementations of the same e-commerce API using FastAPI with different backends:
- SQL implementation using SQLModel ORM
- MongoDB implementation using Beanie ODM
- Supabase implementation with Stripe integration

## Features

- 🔐 User authentication with JWT
- 🛒 Product management (CRUD operations)
- 📄 Order processing and tracking
- 📦 Stock management
- 🔍 Pagination and filtering for product listing
- 🖼️ Image upload support for products
- 🤖 AI-powered RAG chatbot for QA
- 🛠️ Error handling and logging

## Prerequisites

- Python 3.8+
- Database requirements:
  - SQLite (for RDB version)
  - MongoDB (for MongoDB version)
- External services:
  - Supabase account (for Supabase version)
  - Stripe account (for payment processing)
  - Gemini API key (for AI features)

## Installation & Setup

1. Clone the repository
2. Choose your preferred implementation:

### For SQL Implementation:
```sh
cd ecommerce-rdb
pip install -r requirements.txt
python seed.py  # Optional: populate with sample data
python main.py
```

### For MongoDB Implementation:
```sh
cd ecommerce-mongodb
pip install -r requirements.txt
# Ensure MongoDB is running on localhost:27017
python seed.py  # Optional: populate with sample data
python main.py
```

### For Supabase-Stripe Implementation:
```sh
cd ecommerce-supabase-stripe
pip install -r requirements.txt
# Configure .env file with Supabase and Stripe credentials
python seed.py  # Optional: populate with sample data
python main.py
```

## API Endpoints

All implementations share the same API interface:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Store
- `POST /store/products/` - Create new product
- `GET /store/products/` - List all products
- `GET /store/products/{product_id}` - Get product details
- `GET /store/search` - Search products
- `POST /store/orders/` - Create new order
- `GET /store/my-orders` - List user's orders

### Chat
- `POST /chat/faq` - AI-powered RAG for faq

## Key Differences

### RDB Implementation (SQLModel)
- Uses SQLite as database
- Traditional relational data modeling
- Uses SQLModel for type-safe database operations

### MongoDB Implementation (Beanie)
- Uses MongoDB as database
- Leverages Beanie ODM for async operations
- Native support for document-based data model

### Supabase-Stripe Implementation
- Uses Supabase PostgreSQL as database
- Supabase User Authentication
- Supabase Object Storage for images
- Stripe Payment Integration
- Webhook that reliably handle post-payment logic

## Development

The API will be available at `http://localhost:8000` with interactive API documentation at `/docs`.

## Environment Variables

Common environment variables for rdb and mongodb implementations:
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `GOOGLE_API_KEY` - Gemini API KEY
- `MONGO_URI` - MongoDB connection string (default: "mongodb://localhost:27017")

Additional ones for supabase/stripe implementation:
```env
STRIPE_KEY=your_stripe_secret_key
STRIPE_ENDPOINT_SECRET=your_stripe_webhook_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET_URL=your_supabase_bucket_url
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```