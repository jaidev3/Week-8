# Zomato Restaurant Management API - Version 1

A foundational restaurant listing system for a food delivery platform, providing complete CRUD operations for restaurant management.

## Features

### Core Features
- Complete CRUD operations for restaurants
- Restaurant data validation and error handling
- Proper API documentation with FastAPI
- Phone number validation
- Time validation (opening/closing hours)
- Rating validation (0.0-5.0 range)
- Duplicate restaurant name prevention
- Pagination support
- Search functionality by cuisine type
- Active/inactive restaurant filtering

### Restaurant Model
The restaurant model includes the following fields:
- `id` - Primary Key (auto-generated)
- `name` - Required, 3-100 characters, must be unique
- `description` - Optional text
- `cuisine_type` - Required (e.g., "Italian", "Chinese", "Indian")
- `address` - Required
- `phone_number` - Required, with validation (minimum 10 digits)
- `rating` - Float, 0.0-5.0 range, default 0.0
- `is_active` - Boolean, default True
- `opening_time` - Time (required)
- `closing_time` - Time (required, must be after opening_time)
- `created_at` - Timestamp (auto-generated)
- `updated_at` - Timestamp (auto-updated)

## API Endpoints

### Restaurant Management
- `POST /restaurants/` - Create new restaurant
- `GET /restaurants/` - List all restaurants (with pagination)
- `GET /restaurants/{restaurant_id}` - Get specific restaurant
- `PUT /restaurants/{restaurant_id}` - Update restaurant
- `DELETE /restaurants/{restaurant_id}` - Delete restaurant

### Search and Filtering
- `GET /restaurants/search?cuisine={cuisine_type}` - Search by cuisine
- `GET /restaurants/active` - List only active restaurants

### Query Parameters
- `skip` - Number of records to skip (default: 0)
- `limit` - Number of records to return (default: 100, max: 1000)
- `cuisine` - Cuisine type for search (required for search endpoint)

## Technical Stack
- **Framework**: FastAPI
- **Database**: SQLite with async SQLAlchemy
- **Validation**: Pydantic schemas
- **Server**: Uvicorn

## Setup Instructions

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

The API will be available at `http://127.0.0.1:8000`

### API Documentation
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Example Usage

### Create a Restaurant
```bash
curl -X POST "http://127.0.0.1:8000/restaurants/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Spice Garden",
       "description": "Authentic Indian cuisine with traditional flavors",
       "cuisine_type": "Indian",
       "address": "123 Main St, Food City, FC 12345",
       "phone_number": "+1-555-123-4567",
       "rating": 4.5,
       "opening_time": "11:00:00",
       "closing_time": "23:00:00"
     }'
```

### Search Restaurants by Cuisine
```bash
curl "http://127.0.0.1:8000/restaurants/search?cuisine=Italian&skip=0&limit=10"
```

### Get Active Restaurants
```bash
curl "http://127.0.0.1:8000/restaurants/active?skip=0&limit=50"
```

## Validation Rules

### Phone Number
- Must contain at least 10 digits
- Special characters and spaces are allowed but ignored during validation

### Rating
- Must be between 0.0 and 5.0 (inclusive)
- Defaults to 0.0 for new restaurants

### Times
- Opening and closing times are required
- Closing time must be after opening time
- Format: "HH:MM:SS" (24-hour format)

### Restaurant Name
- Must be unique across all restaurants
- 3-100 characters in length

## HTTP Status Codes
- `200` - OK (successful GET, PUT requests)
- `201` - Created (successful POST requests)
- `400` - Bad Request (validation errors, duplicate names)
- `404` - Not Found (restaurant doesn't exist)
- `422` - Unprocessable Entity (validation errors)

## Error Handling
The API provides detailed error messages for:
- Validation failures
- Duplicate restaurant names
- Invalid phone number formats
- Invalid time ranges
- Missing required fields
- Restaurant not found scenarios

## Database
- Uses SQLite database (`zomato.db`)
- Async SQLAlchemy for database operations
- Automatic table creation on startup
- Database sessions with proper rollback handling

## Next Steps
This is Version 1 of the Zomato platform. Future versions will include:
- Menu items management
- Customer management
- Order processing
- Reviews and ratings system
- Advanced business logic

---

**Version**: 1.0.0  
**Last Updated**: December 2024