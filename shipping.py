"""
Shipping API Routes
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/rates")
async def get_shipping_rates():
    """Get shipping rates"""
    return {"message": "Shipping rates endpoint"}

