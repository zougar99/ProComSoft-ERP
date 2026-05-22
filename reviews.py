"""
Reviews API Routes
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.post("/")
async def create_review():
    """Create product review"""
    return {"message": "Review endpoint"}

