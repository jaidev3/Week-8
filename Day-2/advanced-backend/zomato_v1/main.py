from fastapi import FastAPI
from database import create_tables
from routes import router as user_router
import uvicorn

app = FastAPI(
    title="User Management API - Version 1",
    description="Basic CRUD operations with single table",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    await create_tables()

app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "User Management API Version 1"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
