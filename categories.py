"""
Categories API Routes
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/")
async def get_categories():
    """Get all categories"""
    return {"message": "Categories endpoint"}

