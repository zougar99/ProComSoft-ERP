<<<<<<< HEAD
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

=======
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

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
