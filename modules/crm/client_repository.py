"""
Client Repository
Data access operations for clients
"""

from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository
from models.client import Client
from core.exceptions import NotFoundError, DuplicateError
from services.numbering_service import NumberingService


class ClientRepository(BaseRepository):
    """Repository for client CRUD operations"""
    
    def __init__(self):
        super().__init__(table_name='erp_clients', primary_key='id')
    
    def create_client(self, client: Client) -> int:
        """
        Create a new client
        
        Args:
            client: Client model instance
            
        Returns:
            ID of created client
        """
        # Generate code if not provided
        if not client.code:
            client.code = NumberingService.generate_client_code()
        
        # Check for duplicate code
        if client.code and self._code_exists(client.code):
            raise DuplicateError(f"Client with code {client.code} already exists")
        
        data = client.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        client_id = self.create(data)
        return client_id
    
    def get_client(self, client_id: int) -> Optional[Client]:
        """
        Get client by ID
        
        Args:
            client_id: Client ID
            
        Returns:
            Client model or None if not found
        """
        data = self.get_by_id(client_id)
        if data:
            return Client.from_dict(data)
        return None
    
    def get_client_by_code(self, code: str) -> Optional[Client]:
        """
        Get client by code
        
        Args:
            code: Client code
            
        Returns:
            Client model or None if not found
        """
        clients = self.get_all(filters={'code': code}, limit=1)
        if clients:
            return Client.from_dict(clients[0])
        return None
    
    def get_all_clients(self, filters: Optional[Dict[str, Any]] = None, 
                       order_by: str = "name ASC",
                       active_only: bool = False) -> List[Client]:
        """
        Get all clients
        
        Args:
            filters: Additional filters
            order_by: Order by clause
            active_only: Only return active clients
            
        Returns:
            List of Client models
        """
        if filters is None:
            filters = {}
        
        if active_only:
            filters['is_active'] = 1
        
        data_list = self.get_all(filters=filters, order_by=order_by)
        return [Client.from_dict(data) for data in data_list]
    
    def search_clients(self, query: str, active_only: bool = False) -> List[Client]:
        """
        Search clients by name, code, phone, or email
        
        Args:
            query: Search query
            active_only: Only search active clients
            
        Returns:
            List of matching Client models
        """
        try:
            from core.database import get_connection
            
            with get_connection() as conn:
                search_pattern = f"%{query}%"
                sql = """
                    SELECT * FROM erp_clients
                    WHERE (name LIKE ? OR code LIKE ? OR phone LIKE ? OR email LIKE ?)
                """
                params = [search_pattern, search_pattern, search_pattern, search_pattern]
                
                if active_only:
                    sql += " AND is_active = 1"
                
                sql += " ORDER BY name ASC"
                
                cursor = conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [Client.from_dict(dict(row)) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to search clients: {str(e)}")
    
    def update_client(self, client: Client) -> bool:
        """
        Update client
        
        Args:
            client: Client model with updated data
            
        Returns:
            True if update was successful
        """
        if not client.id:
            raise ValueError("Client ID is required for update")
        
        # Check for duplicate code (if code changed)
        if client.code:
            existing = self.get_client_by_code(client.code)
            if existing and existing.id != client.id:
                raise DuplicateError(f"Client with code {client.code} already exists")
        
        data = client.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.update(client.id, data)
    
    def delete_client(self, client_id: int) -> bool:
        """
        Delete client (soft delete by setting is_active = 0)
        
        Args:
            client_id: Client ID
            
        Returns:
            True if deletion was successful
        """
        client = self.get_client(client_id)
        if not client:
            raise NotFoundError(f"Client with ID {client_id} not found")
        
        client.is_active = False
        return self.update_client(client)
    
    def update_balance(self, client_id: int, amount: float) -> bool:
        """
        Update client balance
        
        Args:
            client_id: Client ID
            amount: Amount to add/subtract (positive for increase, negative for decrease)
            
        Returns:
            True if update was successful
        """
        client = self.get_client(client_id)
        if not client:
            raise NotFoundError(f"Client with ID {client_id} not found")
        
        client.balance += amount
        return self.update_client(client)
    
    def _code_exists(self, code: str) -> bool:
        """Check if client code already exists"""
        existing = self.get_client_by_code(code)
        return existing is not None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
