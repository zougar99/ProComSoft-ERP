<<<<<<< HEAD
"""
Users API Routes
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/profile")
async def get_profile():
    """Get user profile"""
    return {"message": "User profile endpoint"}

=======
"""
Users API Routes
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/profile")
async def get_profile():
    """Get user profile"""
    return {"message": "User profile endpoint"}

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
