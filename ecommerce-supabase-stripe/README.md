# FastAPI E-Commerce API

A modern e-commerce API built with FastAPI, Supabase, and Stripe integration.

## Features

- 🔐 User Authentication with Supabase
- 🛍️ Product Management
- 🛒 Shopping Cart & Order System
- 💳 Stripe Payment Integration
- 📦 Product Image Storage with Supabase Storage
- 🔍 Product Search and Filtering
- 📄 Order History and Management

## Tech Stack

- FastAPI
- PostgreSQL (via Supabase)
- SQLModel ORM
- Supabase for Auth and Storage
- Stripe for Payments

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Supabase Account
- Stripe Account

### Environment Setup

Create a `.env` file in the root directory with:

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

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi-supabase-stripe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python seed.py
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login user
- `GET /auth/me` - Get current user

### Store
- `POST /store/products/` - Create new product
- `GET /store/products/` - List all products
- `GET /store/products/{product_id}` - Get product details
- `GET /store/search` - Search products
- `POST /store/orders/` - Create new order
- `GET /store/my-orders` - Get user orders
- `POST /store/webhook` - Stripe webhook endpoint

## Development

To populate the database with test data:

```bash
python seed.py
```

## Security

- JWT-based authentication
- Secure payment processing with Stripe
- Environment variables for sensitive data