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

