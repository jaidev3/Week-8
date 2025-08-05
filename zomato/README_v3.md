# Zomato Food Delivery API - Version 3

A complete food delivery ecosystem built with FastAPI and SQLAlchemy, featuring complex multi-table relationships, order management, customer tracking, and comprehensive analytics.

## 🚀 Features

### Core Functionality
- **Restaurant Management**: Full CRUD operations with advanced search
- **Menu Item Management**: Complete menu lifecycle with availability tracking
- **Customer Management**: Customer profiles and account management
- **Order Processing**: Complete order workflow with status tracking
- **Review System**: Customer reviews and restaurant ratings
- **Analytics Dashboard**: Comprehensive business intelligence

### Advanced Relationships
- **Customer → Orders** (One-to-Many)
- **Restaurant → Orders** (One-to-Many)
- **Order → Order Items → Menu Items** (Many-to-Many with additional data)
- **Customer → Reviews** (One-to-Many)
- **Restaurant → Reviews** (One-to-Many)

### Business Logic
- **Order Status Workflow**: `placed` → `confirmed` → `preparing` → `out_for_delivery` → `delivered` → `cancelled`
- **Smart Calculations**: Automatic order total calculation
- **Review Validation**: Reviews only for completed orders
- **Rating Updates**: Automatic restaurant rating recalculation
- **Inventory Checks**: Menu item availability validation

## 🏗️ Architecture

### Database Models
- **Restaurant**: Core restaurant information with operating hours and ratings
- **MenuItem**: Menu items with pricing and dietary information
- **Customer**: Customer profiles with contact information
- **Order**: Order management with status tracking
- **OrderItem**: Association table with quantity and pricing at time of order
- **Review**: Customer reviews with ratings and comments

### Complex Relationships
```
Customer ──┬── Orders ──┬── OrderItems ──── MenuItems
           │            │
           └── Reviews   └── Restaurant ──┬── MenuItems
                                         │
                                         └── Reviews
```

## 📋 API Endpoints

### Customer Management
- `POST /customers/` - Create new customer
- `GET /customers/` - List all customers
- `GET /customers/{id}` - Get specific customer
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer
- `GET /customers/{id}/orders` - Customer's order history
- `GET /customers/{id}/reviews` - Customer's reviews
- `GET /customers/{id}/analytics` - Customer analytics

### Order Management
- `POST /customers/{customer_id}/orders/` - Place new order
- `GET /orders/{order_id}` - Get order with full details
- `PUT /orders/{order_id}/status` - Update order status
- `GET /customers/{customer_id}/orders` - Customer's order history
- `GET /restaurants/{restaurant_id}/orders` - Restaurant's orders
- `GET /orders/` - List all orders with filtering

### Review System
- `POST /orders/{order_id}/review` - Add review after order completion
- `GET /restaurants/{restaurant_id}/reviews` - Get restaurant reviews
- `GET /customers/{customer_id}/reviews` - Get customer's reviews

### Advanced Restaurant Features
- `GET /restaurants/search` - Advanced search (cuisine, rating, location)
- `GET /restaurants/trending` - Trending restaurants
- `GET /restaurants/{id}/reviews` - Restaurant reviews
- `GET /restaurants/{id}/analytics` - Restaurant performance metrics

### Analytics Endpoints
- `GET /analytics/restaurants/{restaurant_id}` - Restaurant analytics
- `GET /analytics/customers/{customer_id}` - Customer analytics

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zomato-api-v3
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the API**
   - API Documentation: http://127.0.0.1:8000/docs
   - Alternative Docs: http://127.0.0.1:8000/redoc
   - API Root: http://127.0.0.1:8000/

## 🧪 Complete Testing Examples

### 1. Create Customer
```bash
curl -X POST "http://127.0.0.1:8000/customers/" \
-H "Content-Type: application/json" \
-d '{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1-234-567-8900",
  "address": "123 Main St, City, State 12345"
}'
```

### 2. Place Order
```bash
curl -X POST "http://127.0.0.1:8000/customers/1/orders" \
-H "Content-Type: application/json" \
-d '{
  "restaurant_id": 1,
  "delivery_address": "123 Main St, City, State 12345",
  "special_instructions": "Ring doorbell twice",
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2,
      "special_requests": "Extra spicy"
    },
    {
      "menu_item_id": 2,
      "quantity": 1
    }
  ]
}'
```

### 3. Update Order Status
```bash
curl -X PUT "http://127.0.0.1:8000/orders/1/status" \
-H "Content-Type: application/json" \
-d '{
  "order_status": "confirmed"
}'
```

### 4. Add Review
```bash
curl -X POST "http://127.0.0.1:8000/orders/1/review?customer_id=1" \
-H "Content-Type: application/json" \
-d '{
  "rating": 5,
  "comment": "Excellent food and fast delivery!"
}'
```

### 5. Advanced Restaurant Search
```bash
curl "http://127.0.0.1:8000/restaurants/search?cuisine=Italian&min_rating=4.0&location=downtown"
```

### 6. Get Analytics
```bash
curl "http://127.0.0.1:8000/analytics/restaurants/1"
curl "http://127.0.0.1:8000/analytics/customers/1"
```

## 🚦 Order Status Workflow

```
PLACED ──→ CONFIRMED ──→ PREPARING ──→ OUT_FOR_DELIVERY ──→ DELIVERED
   │            │             │               │
   ↓            ↓             ↓               ↓
CANCELLED   CANCELLED    CANCELLED       CANCELLED
```

### Valid Status Transitions
- `placed` → `confirmed`, `cancelled`
- `confirmed` → `preparing`, `cancelled`
- `preparing` → `out_for_delivery`, `cancelled`
- `out_for_delivery` → `delivered`, `cancelled`
- `delivered` → (final state)
- `cancelled` → (final state)

## 📊 Business Intelligence

### Restaurant Metrics
- Revenue tracking
- Order volume analysis
- Customer retention
- Popular items identification
- Performance benchmarking

### Customer Insights
- Spending behavior
- Preference analysis
- Loyalty scoring
- Churn prediction
- Lifetime value calculation

## 🔒 Data Integrity & Validation

### Business Rules
- Reviews only for completed orders
- Order items must belong to the same restaurant
- Menu items must be available when ordered
- Email uniqueness for customers
- Status transition validation

### Data Validation
- Email format validation
- Phone number format checking
- Rating bounds (1-5 stars)
- Positive pricing constraints
- Address completeness

---

**Version 3.0.0** - Complete Food Delivery Ecosystem with Advanced Multi-table Relationships