<<<<<<< HEAD
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

=======
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

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
