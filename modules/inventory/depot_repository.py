"""
Depot Repository
Data access operations for depots
"""

from typing import Optional, List
from repositories.base_repository import BaseRepository
from models.depot import Depot
from core.exceptions import NotFoundError, DuplicateError
from services.numbering_service import NumberingService


class DepotRepository(BaseRepository):
    """Repository for depot CRUD operations"""
    
    def __init__(self):
        super().__init__(table_name='erp_depots', primary_key='id')
    
    def create_depot(self, depot: Depot) -> int:
        """Create a new depot"""
        if not depot.code:
            depot.code = NumberingService.generate_number('depot', 'erp_depots', 'code')
        
        if depot.code and self._code_exists(depot.code):
            raise DuplicateError(f"Depot with code {depot.code} already exists")
        
        # If this is main depot, unset other main depots
        if depot.is_main:
            self._unset_main_depots()
        
        data = depot.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.create(data)
    
    def get_depot(self, depot_id: int) -> Optional[Depot]:
        """Get depot by ID"""
        data = self.get_by_id(depot_id)
        return Depot.from_dict(data) if data else None
    
    def get_main_depot(self) -> Optional[Depot]:
        """Get main depot"""
        depots = self.get_all(filters={'is_main': 1}, limit=1)
        return Depot.from_dict(depots[0]) if depots else None
    
    def get_all_depots(self, active_only: bool = False,
                      order_by: str = "name ASC") -> List[Depot]:
        """Get all depots"""
        filters = {}
        if active_only:
            filters['is_active'] = 1
        
        data_list = self.get_all(filters=filters, order_by=order_by)
        return [Depot.from_dict(data) for data in data_list]
    
    def update_depot(self, depot: Depot) -> bool:
        """Update depot"""
        if not depot.id:
            raise ValueError("Depot ID is required for update")
        
        # If setting as main, unset other main depots
        if depot.is_main:
            self._unset_main_depots(exclude_id=depot.id)
        
        data = depot.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.update(depot.id, data)
    
    def delete_depot(self, depot_id: int) -> bool:
        """Delete depot (soft delete)"""
        depot = self.get_depot(depot_id)
        if not depot:
            raise NotFoundError(f"Depot with ID {depot_id} not found")
        
        depot.is_active = False
        return self.update_depot(depot)
    
    def _code_exists(self, code: str) -> bool:
        """Check if depot code exists"""
        depots = self.get_all(filters={'code': code}, limit=1)
        return len(depots) > 0
    
    def _unset_main_depots(self, exclude_id: Optional[int] = None):
        """Unset all main depots except exclude_id"""
        from core.database import get_connection
        
        with get_connection() as conn:
            if exclude_id:
                sql = "UPDATE erp_depots SET is_main = 0 WHERE is_main = 1 AND id != ?"
                conn.execute(sql, (exclude_id,))
            else:
                sql = "UPDATE erp_depots SET is_main = 0 WHERE is_main = 1"
                conn.execute(sql)
            conn.commit()
    
    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
