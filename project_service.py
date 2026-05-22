"""
Project Service - إدارة المشاريع/الأعمال
"""

from datetime import datetime
from database.init import get_database

class ProjectService:
    @staticmethod
    def generate_project_code():
        """Generate unique project code"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('SELECT code FROM projects ORDER BY id DESC LIMIT 1')
        last_project = cursor.fetchone()
        
        if last_project:
            try:
                last_num = int(last_project['code'].split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'PRJ-{new_num:05d}'
    
    @staticmethod
    def create(project_data):
        """Create new project"""
        db = get_database()
        cursor = db.cursor()
        
        # Generate code if not provided
        if not project_data.get('code'):
            project_data['code'] = ProjectService.generate_project_code()
        
        cursor.execute('''
            INSERT INTO projects (
                code, name, name_ar, name_fr, customer_id,
                start_date, end_date, status, budget, actual_cost,
                progress_percent, description, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_data['code'],
            project_data['name'],
            project_data.get('name_ar'),
            project_data.get('name_fr'),
            project_data.get('customer_id'),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('status', 'active'),
            project_data.get('budget', 0),
            project_data.get('actual_cost', 0),
            project_data.get('progress_percent', 0),
            project_data.get('description'),
            project_data.get('created_by')
        ))
        
        db.commit()
        return ProjectService.get(cursor.lastrowid)
    
    @staticmethod
    def get(project_id):
        """Get project by ID"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT p.*, c.name as customer_name, c.code as customer_code,
                   u.full_name as created_by_name
            FROM projects p
            LEFT JOIN customers c ON p.customer_id = c.id
            LEFT JOIN users u ON p.created_by = u.id
            WHERE p.id = ?
        ''', (project_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        project_dict = dict(row)
        
        # Get follow-ups
        cursor.execute('''
            SELECT f.*, u.full_name as created_by_name
            FROM project_followups f
            LEFT JOIN users u ON f.created_by = u.id
            WHERE f.project_id = ?
            ORDER BY f.followup_date DESC
        ''', (project_id,))
        
        project_dict['followups'] = [dict(row) for row in cursor.fetchall()]
        
        return project_dict
    
    @staticmethod
    def list(filters=None):
        """List projects with filters"""
        db = get_database()
        cursor = db.cursor()
        
        query = '''
            SELECT p.*, c.name as customer_name, c.code as customer_code
            FROM projects p
            LEFT JOIN customers c ON p.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('customer_id'):
                query += ' AND p.customer_id = ?'
                params.append(filters['customer_id'])
            
            if filters.get('status'):
                query += ' AND p.status = ?'
                params.append(filters['status'])
        
        query += ' ORDER BY p.created_at DESC'
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(project_id, project_data):
        """Update project"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE projects SET
                name = ?, name_ar = ?, name_fr = ?, customer_id = ?,
                start_date = ?, end_date = ?, status = ?,
                budget = ?, actual_cost = ?, progress_percent = ?,
                description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            project_data.get('name'),
            project_data.get('name_ar'),
            project_data.get('name_fr'),
            project_data.get('customer_id'),
            project_data.get('start_date'),
            project_data.get('end_date'),
            project_data.get('status'),
            project_data.get('budget', 0),
            project_data.get('actual_cost', 0),
            project_data.get('progress_percent', 0),
            project_data.get('description'),
            project_id
        ))
        
        db.commit()
        return ProjectService.get(project_id)
    
    @staticmethod
    def delete(project_id):
        """Delete project"""
        db = get_database()
        db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        db.commit()
        return True
    
    @staticmethod
    def add_followup(project_id, followup_data):
        """Add follow-up to project"""
        db = get_database()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO project_followups (
                project_id, followup_date, title, description, status, created_by
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            followup_data['followup_date'],
            followup_data['title'],
            followup_data.get('description'),
            followup_data.get('status'),
            followup_data.get('created_by')
        ))
        
        db.commit()
        return ProjectService.get(project_id)

