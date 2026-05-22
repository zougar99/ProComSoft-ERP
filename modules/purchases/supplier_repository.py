"""
Supplier Repository
Data access operations for suppliers
"""

from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository
from models.supplier import Supplier
from core.exceptions import NotFoundError, DuplicateError
from services.numbering_service import NumberingService


class SupplierRepository(BaseRepository):
    """Repository for supplier CRUD operations"""
    
    def __init__(self):
        super().__init__(table_name='erp_suppliers', primary_key='id')
    
    def create_supplier(self, supplier: Supplier) -> int:
        """Create a new supplier"""
        if not supplier.code:
            supplier.code = NumberingService.generate_supplier_code()
        
        if supplier.code and self._code_exists(supplier.code):
            raise DuplicateError(f"Supplier with code {supplier.code} already exists")
        
        data = supplier.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.create(data)
    
    def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        data = self.get_by_id(supplier_id)
        return Supplier.from_dict(data) if data else None
    
    def get_supplier_by_code(self, code: str) -> Optional[Supplier]:
        """Get supplier by code"""
        suppliers = self.get_all(filters={'code': code}, limit=1)
        return Supplier.from_dict(suppliers[0]) if suppliers else None
    
    def get_all_suppliers(self, filters: Optional[Dict[str, Any]] = None,
                         order_by: str = "name ASC",
                         active_only: bool = False) -> List[Supplier]:
        """Get all suppliers"""
        if filters is None:
            filters = {}
        if active_only:
            filters['is_active'] = 1
        
        data_list = self.get_all(filters=filters, order_by=order_by)
        return [Supplier.from_dict(data) for data in data_list]
    
    def search_suppliers(self, query: str, active_only: bool = False) -> List[Supplier]:
        """Search suppliers"""
        from core.database import get_connection
        
        with get_connection() as conn:
            search_pattern = f"%{query}%"
            sql = """
                SELECT * FROM erp_suppliers
                WHERE (name LIKE ? OR code LIKE ? OR phone LIKE ? OR email LIKE ?)
            """
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
            
            if active_only:
                sql += " AND is_active = 1"
            
            sql += " ORDER BY name ASC"
            
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [Supplier.from_dict(dict(row)) for row in rows]
    
    def update_supplier(self, supplier: Supplier) -> bool:
        """Update supplier"""
        if not supplier.id:
            raise ValueError("Supplier ID is required for update")
        
        if supplier.code:
            existing = self.get_supplier_by_code(supplier.code)
            if existing and existing.id != supplier.id:
                raise DuplicateError(f"Supplier with code {supplier.code} already exists")
        
        data = supplier.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.update(supplier.id, data)
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Delete supplier (soft delete)"""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        supplier.is_active = False
        return self.update_supplier(supplier)
    
    def update_balance(self, supplier_id: int, amount: float) -> bool:
        """Update supplier balance"""
        supplier = self.get_supplier(supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier with ID {supplier_id} not found")
        
        supplier.balance += amount
        return self.update_supplier(supplier)
    
    def _code_exists(self, code: str) -> bool:
        """Check if supplier code exists"""
        return self.get_supplier_by_code(code) is not None
    
    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
