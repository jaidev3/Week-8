from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database import get_db
from schemas import MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemWithRestaurant
import crud

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(menu_item: MenuItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new menu item"""
    try:
        return await crud.create_menu_item(db=db, menu_item=menu_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/", response_model=List[MenuItemResponse])
async def read_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all menu items with pagination"""
    return await crud.get_menu_items(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[MenuItemResponse])
async def search_menu_items(
    category: Optional[str] = Query(None, description="Category to filter by"),
    vegetarian: Optional[bool] = Query(None, description="Filter by vegetarian items"),
    vegan: Optional[bool] = Query(None, description="Filter by vegan items"),
    available: Optional[bool] = Query(None, description="Filter by availability"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Search menu items by category and dietary preferences"""
    return await crud.search_menu_items(
        db, 
        category=category,
        vegetarian=vegetarian,
        vegan=vegan,
        available=available,
        skip=skip, 
        limit=limit
    )

@router.get("/{item_id}", response_model=MenuItemResponse)
async def read_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific menu item by ID"""
    db_menu_item = await crud.get_menu_item(db, item_id=item_id)
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

@router.get("/{item_id}/with-restaurant", response_model=MenuItemWithRestaurant)
async def read_menu_item_with_restaurant(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get menu item with restaurant details"""
    db_menu_item = await crud.get_menu_item_with_restaurant(db, item_id=item_id)
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: int, 
    menu_item: MenuItemUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update a menu item"""
    try:
        db_menu_item = await crud.update_menu_item(db, item_id=item_id, menu_item_update=menu_item)
        if db_menu_item is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return db_menu_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/{item_id}", response_model=MenuItemResponse)
async def delete_menu_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a menu item"""
    db_menu_item = await crud.delete_menu_item(db, item_id=item_id)
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

