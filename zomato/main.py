from fastapi import FastAPI
from database import create_tables
from routes import router as restaurant_router
import uvicorn

app = FastAPI(
    title="Zomato Restaurant Management API - Version 1",
    description="Basic restaurant CRUD operations with single table",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    await create_tables()

app.include_router(restaurant_router)

@app.get("/")
async def root():
    return {
        "message": "Zomato Restaurant Management API Version 1",
        "description": "Food delivery platform - Restaurant management system",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
