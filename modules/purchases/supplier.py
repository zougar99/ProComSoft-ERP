"""
Supplier Model
Data model for suppliers/vendors
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Supplier:
    """Supplier data model"""
    
    id: Optional[int] = None
    code: Optional[str] = None
    name: str = ""
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Morocco"
    tax_id: Optional[str] = None
    payment_terms: int = 30  # Days
    balance: float = 0.0  # Amount owed to supplier
    is_active: bool = True
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert supplier to dictionary for database operations"""
        return {
            'code': self.code,
            'name': self.name,
            'company_name': self.company_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'tax_id': self.tax_id,
            'payment_terms': self.payment_terms,
            'balance': self.balance,
            'is_active': 1 if self.is_active else 0,
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Supplier':
        """Create supplier from dictionary (from database)"""
        return cls(
            id=data.get('id'),
            code=data.get('code'),
            name=data.get('name', ''),
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country', 'Morocco'),
            tax_id=data.get('tax_id'),
            payment_terms=data.get('payment_terms', 30),
            balance=data.get('balance', 0.0) or 0.0,
            is_active=bool(data.get('is_active', 1)),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
