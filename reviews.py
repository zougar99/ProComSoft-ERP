<<<<<<< HEAD
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

=======
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

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
