from fastapi import FastAPI
from database import create_tables
from routes.restaurants import router as restaurant_router
from routes.menu_items import router as menu_items_router
from routes.customers import router as customer_router
from routes.orders import router as order_router
from routes.reviews import router as review_router
from routes.analytics import router as analytics_router
import uvicorn

app = FastAPI(
    title="Zomato Food Delivery API - Version 3",
    description="Complete Food Delivery Ecosystem with Complex Multi-table Relationships",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    await create_tables()

# Include all routers
app.include_router(restaurant_router)
app.include_router(menu_items_router)
app.include_router(customer_router)
app.include_router(order_router)
app.include_router(review_router)
app.include_router(analytics_router)

@app.get("/")
async def root():
    return {
        "message": "Zomato Food Delivery API Version 3",
        "description": "Complete food delivery ecosystem with customers, orders, delivery tracking, and reviews",
        "version": "3.0.0",
        "docs": "/docs",
        "features": [
            "Restaurant & Menu Management",
            "Customer Management",
            "Order Processing & Status Tracking",
            "Review & Rating System",
            "Complex Multi-table Relationships",
            "Advanced Analytics & Reporting",
            "Restaurant Search & Filtering",
            "Order History & Tracking",
            "Business Intelligence Dashboard",
            "Performance Metrics & KPIs"
        ],
        "relationships": [
            "Customer → Many Orders (One-to-Many)",
            "Restaurant → Many Orders (One-to-Many)",
            "Order → Many Order Items → Many Menu Items (Many-to-Many with additional data)",
            "Customer → Many Reviews (One-to-Many)",
            "Restaurant → Many Reviews (One-to-Many)"
        ],
        "endpoints": {
            "customers": "/customers",
            "orders": "/orders",
            "reviews": "/reviews",
            "analytics": "/analytics",
            "restaurants": "/restaurants",
            "menu_items": "/menu-items"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
