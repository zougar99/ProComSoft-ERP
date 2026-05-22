"""
Depot Model
Data model for depots/warehouses
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Depot:
    """Depot (Warehouse) data model"""
    
    id: Optional[int] = None
    code: Optional[str] = None
    name: str = ""
    address: Optional[str] = None
    is_main: bool = False
    is_active: bool = True
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert depot to dictionary for database operations"""
        return {
            'code': self.code,
            'name': self.name,
            'address': self.address,
            'is_main': 1 if self.is_main else 0,
            'is_active': 1 if self.is_active else 0,
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Depot':
        """Create depot from dictionary (from database)"""
        return cls(
            id=data.get('id'),
            code=data.get('code'),
            name=data.get('name', ''),
            address=data.get('address'),
            is_main=bool(data.get('is_main', 0)),
            is_active=bool(data.get('is_active', 1)),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )
