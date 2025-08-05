from fastapi import FastAPI
from database import create_tables
from routes.restaurants import router as restaurant_router
from routes.menu_items import router as menu_items_router
import uvicorn

app = FastAPI(
    title="Zomato Restaurant Management API - Version 2",
    description="Restaurant-Menu System with One-to-Many Relationships",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    await create_tables()

app.include_router(restaurant_router)
app.include_router(menu_items_router)

@app.get("/")
async def root():
    return {
        "message": "Zomato Restaurant Management API Version 2",
        "description": "Food delivery platform - Restaurant-Menu management system with relationships",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "Restaurant CRUD operations",
            "Menu item management",
            "One-to-many relationships",
            "Advanced querying with relationships",
            "Dietary preference filtering"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
