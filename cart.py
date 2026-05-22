"""
Shopping Cart API Routes
Cart management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from database.connection import get_db
from database.schema import CartItem, Product, ProductVariant, User
from core.security import get_current_user

router = APIRouter()


class CartItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    variant_id: Optional[UUID]
    quantity: int
    price: float
    
    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = 1


@router.get("/", response_model=list[CartItemResponse])
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's shopping cart"""
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    return cart_items


@router.post("/", response_model=CartItemResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Verify variant if provided
    if item_data.variant_id:
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == item_data.variant_id
        ).first()
        if not variant:
            raise HTTPException(status_code=404, detail="Variant not found")
        price = variant.price or product.price
    else:
        price = product.price
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_data.product_id,
        CartItem.variant_id == item_data.variant_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item_data.quantity
        existing_item.price = price
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    # Create new cart item
    cart_item = CartItem(
        user_id=current_user.id,
        product_id=item_data.product_id,
        variant_id=item_data.variant_id,
        quantity=item_data.quantity,
        price=price
    )
    
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    return cart_item


@router.put("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        raise HTTPException(status_code=200, detail="Item removed from cart")
    
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    
    return cart_item


@router.delete("/{item_id}")
async def remove_from_cart(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart"}


@router.delete("/")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Cart cleared"}

