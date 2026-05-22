<<<<<<< HEAD
"""
Orders API Routes
Order management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.schema import Order, OrderItem, CartItem, User, OrderStatus
from core.security import get_current_user

router = APIRouter()


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: str
    subtotal: float
    tax_amount: float
    shipping_amount: float
    total: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    shipping_address_id: UUID
    billing_address_id: UUID
    notes: Optional[str] = None


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart"""
    # Get cart items
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in cart_items)
    tax_amount = subtotal * 0.19  # 19% VAT (configurable)
    shipping_amount = 0  # Calculate based on shipping method
    total = subtotal + tax_amount + shipping_amount
    
    # Generate order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())}"
    
    # Create order
    order = Order(
        order_number=order_number,
        user_id=current_user.id,
        shipping_address_id=order_data.shipping_address_id,
        billing_address_id=order_data.billing_address_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total=total,
        notes=order_data.notes,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    db.flush()
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            variant_id=cart_item.variant_id,
            sku=cart_item.product.sku,
            name=cart_item.product.name,
            quantity=cart_item.quantity,
            price=cart_item.price,
            total=cart_item.price * cart_item.quantity
        )
        db.add(order_item)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

=======
"""
Orders API Routes
Order management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from database.connection import get_db
from database.schema import Order, OrderItem, CartItem, User, OrderStatus
from core.security import get_current_user

router = APIRouter()


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: str
    subtotal: float
    tax_amount: float
    shipping_amount: float
    total: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    shipping_address_id: UUID
    billing_address_id: UUID
    notes: Optional[str] = None


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart"""
    # Get cart items
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in cart_items)
    tax_amount = subtotal * 0.19  # 19% VAT (configurable)
    shipping_amount = 0  # Calculate based on shipping method
    total = subtotal + tax_amount + shipping_amount
    
    # Generate order number
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp())}"
    
    # Create order
    order = Order(
        order_number=order_number,
        user_id=current_user.id,
        shipping_address_id=order_data.shipping_address_id,
        billing_address_id=order_data.billing_address_id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total=total,
        notes=order_data.notes,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    db.flush()
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            variant_id=cart_item.variant_id,
            sku=cart_item.product.sku,
            name=cart_item.product.name,
            quantity=cart_item.quantity,
            price=cart_item.price,
            total=cart_item.price * cart_item.quantity
        )
        db.add(order_item)
    
    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
