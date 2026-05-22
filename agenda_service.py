"""
Agenda Service - إدارة الأجندة/المواعيد
"""

from datetime import datetime
from database.init import get_database

class AgendaService:
    @staticmethod
    def create(event_data):
        """Create new event"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO agenda_events (
                title, description, event_date, end_date,
                event_type, category, customer_id, project_id,
                location, reminder_minutes, is_completed, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['title'],
            event_data.get('description'),
            event_data['event_date'],
            event_data.get('end_date'),
            event_data.get('event_type', 'meeting'),
            event_data.get('category'),
            event_data.get('customer_id'),
            event_data.get('project_id'),
            event_data.get('location'),
            event_data.get('reminder_minutes'),
            event_data.get('is_completed', 0),
            event_data.get('created_by')
        ))
        
        db.commit()
        return AgendaService.get(cursor.lastrowid)
    
    @staticmethod
    def get(event_id):
        """Get event by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT e.*, 
                   c.name as customer_name, c.code as customer_code,
                   p.name as project_name, p.code as project_code,
                   u.full_name as created_by_name
            FROM agenda_events e
            LEFT JOIN customers c ON e.customer_id = c.id
            LEFT JOIN projects p ON e.project_id = p.id
            LEFT JOIN users u ON e.created_by = u.id
            WHERE e.id = ?
        ''', (event_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def list(filters=None):
        """List events with filters"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT e.*, 
                   c.name as customer_name, c.code as customer_code,
                   p.name as project_name, p.code as project_code
            FROM agenda_events e
            LEFT JOIN customers c ON e.customer_id = c.id
            LEFT JOIN projects p ON e.project_id = p.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('customer_id'):
                query += ' AND e.customer_id = ?'
                params.append(filters['customer_id'])
            
            if filters.get('project_id'):
                query += ' AND e.project_id = ?'
                params.append(filters['project_id'])
            
            if filters.get('event_type'):
                query += ' AND e.event_type = ?'
                params.append(filters['event_type'])
            
            if filters.get('date_from'):
                query += ' AND e.event_date >= ?'
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += ' AND e.event_date <= ?'
                params.append(filters['date_to'])
            
            if filters.get('is_completed') is not None:
                query += ' AND e.is_completed = ?'
                params.append(filters['is_completed'])
        
        query += ' ORDER BY e.event_date ASC, e.id DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(event_id, event_data):
        """Update event"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE agenda_events SET
                title = ?, description = ?, event_date = ?, end_date = ?,
                event_type = ?, category = ?, customer_id = ?, project_id = ?,
                location = ?, reminder_minutes = ?, is_completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            event_data.get('title'),
            event_data.get('description'),
            event_data.get('event_date'),
            event_data.get('end_date'),
            event_data.get('event_type'),
            event_data.get('category'),
            event_data.get('customer_id'),
            event_data.get('project_id'),
            event_data.get('location'),
            event_data.get('reminder_minutes'),
            event_data.get('is_completed', 0),
            event_id
        ))
        
        db.commit()
        return AgendaService.get(event_id)
    
    @staticmethod
    def delete(event_id):
        """Delete event"""
        db = get_database()
        db.execute('DELETE FROM agenda_events WHERE id = ?', (event_id,))
        db.commit()
        return True
    
    @staticmethod
    def mark_completed(event_id, is_completed=True):
        """Mark event as completed or not"""
        db = get_database()
        db.execute('''
            UPDATE agenda_events 
            SET is_completed = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_completed else 0, event_id))
        db.commit()
        return AgendaService.get(event_id)

