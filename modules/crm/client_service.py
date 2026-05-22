"""
Client Service
Business logic for client operations
"""

from typing import Optional, List, Tuple
from models.client import Client
from repositories.client_repository import ClientRepository
from core.validators import (
    validate_required, validate_email, validate_phone,
    validate_credit_limit
)
from core.exceptions import ValidationError, BusinessLogicError
from services.numbering_service import NumberingService


class ClientService:
    """Service for client business logic"""
    
    def __init__(self):
        self.repository = ClientRepository()
    
    def create_client(self, client_data: dict) -> Tuple[Client, List[str]]:
        """
        Create a new client with validation
        
        Args:
            client_data: Dictionary with client data
            
        Returns:
            Tuple of (Client model, list of validation errors)
        """
        errors = []
        
        # Validate required fields
        name_valid, name_error = validate_required(client_data.get('name'), 'Name')
        if not name_valid:
            errors.append(name_error)
        
        # Validate email if provided
        if client_data.get('email'):
            email_valid, email_error = validate_email(client_data.get('email'))
            if not email_valid:
                errors.append(email_error)
        
        # Validate phone if provided
        if client_data.get('phone'):
            phone_valid, phone_error = validate_phone(client_data.get('phone'))
            if not phone_valid:
                errors.append(phone_error)
        
        # Validate credit limit
        credit_limit = client_data.get('credit_limit', 0) or 0
        balance = client_data.get('balance', 0) or 0
        credit_valid, credit_error = validate_credit_limit(credit_limit, balance)
        if not credit_valid:
            errors.append(credit_error)
        
        if errors:
            return None, errors
        
        # Create client model
        client = Client(
            name=client_data.get('name', '').strip(),
            company_name=client_data.get('company_name'),
            phone=client_data.get('phone'),
            email=client_data.get('email'),
            address=client_data.get('address'),
            city=client_data.get('city'),
            postal_code=client_data.get('postal_code'),
            country=client_data.get('country', 'Morocco'),
            tax_id=client_data.get('tax_id'),
            payment_terms=client_data.get('payment_terms', 30),
            credit_limit=float(credit_limit),
            balance=float(balance),
            is_active=client_data.get('is_active', True),
            notes=client_data.get('notes'),
        )
        
        # Generate code if not provided
        if not client_data.get('code'):
            client.code = NumberingService.generate_client_code()
        else:
            client.code = client_data.get('code')
        
        try:
            client_id = self.repository.create_client(client)
            client.id = client_id
            return client, []
        except Exception as e:
            errors.append(str(e))
            return None, errors
    
    def update_client(self, client_id: int, client_data: dict) -> Tuple[Optional[Client], List[str]]:
        """
        Update client with validation
        
        Args:
            client_id: Client ID
            client_data: Dictionary with updated client data
            
        Returns:
            Tuple of (Client model, list of validation errors)
        """
        # Get existing client
        client = self.repository.get_client(client_id)
        if not client:
            return None, [f"Client with ID {client_id} not found"]
        
        errors = []
        
        # Validate name if provided
        if 'name' in client_data:
            name_valid, name_error = validate_required(client_data.get('name'), 'Name')
            if not name_valid:
                errors.append(name_error)
            else:
                client.name = client_data.get('name', '').strip()
        
        # Validate email if provided
        if 'email' in client_data and client_data.get('email'):
            email_valid, email_error = validate_email(client_data.get('email'))
            if not email_valid:
                errors.append(email_error)
            else:
                client.email = client_data.get('email')
        
        # Validate phone if provided
        if 'phone' in client_data and client_data.get('phone'):
            phone_valid, phone_error = validate_phone(client_data.get('phone'))
            if not phone_valid:
                errors.append(phone_error)
            else:
                client.phone = client_data.get('phone')
        
        # Update other fields
        if 'company_name' in client_data:
            client.company_name = client_data.get('company_name')
        if 'address' in client_data:
            client.address = client_data.get('address')
        if 'city' in client_data:
            client.city = client_data.get('city')
        if 'postal_code' in client_data:
            client.postal_code = client_data.get('postal_code')
        if 'country' in client_data:
            client.country = client_data.get('country', 'Morocco')
        if 'tax_id' in client_data:
            client.tax_id = client_data.get('tax_id')
        if 'payment_terms' in client_data:
            client.payment_terms = client_data.get('payment_terms', 30)
        if 'notes' in client_data:
            client.notes = client_data.get('notes')
        
        # Validate credit limit if provided
        if 'credit_limit' in client_data:
            credit_limit = client_data.get('credit_limit', 0) or 0
            credit_valid, credit_error = validate_credit_limit(float(credit_limit), client.balance)
            if not credit_error:
                client.credit_limit = float(credit_limit)
            else:
                errors.append(credit_error)
        
        if errors:
            return None, errors
        
        try:
            success = self.repository.update_client(client)
            if success:
                return self.repository.get_client(client_id), []
            else:
                return None, ["Failed to update client"]
        except Exception as e:
            errors.append(str(e))
            return None, errors
    
    def get_client(self, client_id: int) -> Optional[Client]:
        """Get client by ID"""
        return self.repository.get_client(client_id)
    
    def get_all_clients(self, active_only: bool = False, order_by: str = "name ASC") -> List[Client]:
        """Get all clients"""
        return self.repository.get_all_clients(active_only=active_only, order_by=order_by)
    
    def search_clients(self, query: str, active_only: bool = False) -> List[Client]:
        """Search clients"""
        if not query or not query.strip():
            return self.get_all_clients(active_only=active_only)
        return self.repository.search_clients(query.strip(), active_only=active_only)
    
    def delete_client(self, client_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete client (soft delete)
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            success = self.repository.delete_client(client_id)
            return success, None
        except Exception as e:
            return False, str(e)
    
    def update_balance(self, client_id: int, amount: float) -> Tuple[bool, Optional[str]]:
        """
        Update client balance (for payments/invoices)
        
        Args:
            client_id: Client ID
            amount: Amount to add (positive) or subtract (negative)
            
        Returns:
            Tuple of (success, error_message)
        """
        client = self.repository.get_client(client_id)
        if not client:
            return False, "Client not found"
        
        new_balance = client.balance + amount
        
        # Check credit limit
        if client.credit_limit > 0 and new_balance > client.credit_limit:
            return False, f"Balance would exceed credit limit ({client.credit_limit})"
        
        try:
            success = self.repository.update_balance(client_id, amount)
            return success, None
        except Exception as e:
            return False, str(e)
