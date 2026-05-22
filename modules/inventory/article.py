"""
Article Model
Data model for articles/products/materials
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    """Article (Product/Material/Service) data model"""
    
    id: Optional[int] = None
    code: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    category: Optional[str] = None  # Material, Product, Service
    unit: str = "PCS"  # PCS, KG, M, M2, H
    purchase_price: float = 0.0
    selling_price: float = 0.0
    min_stock: float = 0.0
    max_stock: float = 0.0
    current_stock: float = 0.0  # Calculated from movements
    depot_id: Optional[int] = None
    barcode: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert article to dictionary for database operations"""
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'unit': self.unit,
            'purchase_price': self.purchase_price,
            'selling_price': self.selling_price,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'current_stock': self.current_stock,
            'depot_id': self.depot_id,
            'barcode': self.barcode,
            'is_active': 1 if self.is_active else 0,
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """Create article from dictionary (from database)"""
        return cls(
            id=data.get('id'),
            code=data.get('code'),
            name=data.get('name', ''),
            description=data.get('description'),
            category=data.get('category'),
            unit=data.get('unit', 'PCS'),
            purchase_price=data.get('purchase_price', 0.0) or 0.0,
            selling_price=data.get('selling_price', 0.0) or 0.0,
            min_stock=data.get('min_stock', 0.0) or 0.0,
            max_stock=data.get('max_stock', 0.0) or 0.0,
            current_stock=data.get('current_stock', 0.0) or 0.0,
            depot_id=data.get('depot_id'),
            barcode=data.get('barcode'),
            is_active=bool(data.get('is_active', 1)),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
    
    def is_low_stock(self) -> bool:
        """Check if article is below minimum stock"""
        if self.min_stock <= 0:
            return False
        return self.current_stock < self.min_stock
    
    def is_over_stock(self) -> bool:
        """Check if article exceeds maximum stock"""
        if self.max_stock <= 0:
            return False
        return self.current_stock > self.max_stock
    
    def get_stock_value(self) -> float:
        """Get stock value (current_stock * purchase_price)"""
        return self.current_stock * self.purchase_price
