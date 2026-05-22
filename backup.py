<<<<<<< HEAD
"""
Backup and restore utilities
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    """Handle database backups and restores"""
    
    def __init__(self, db_path='data/pos_system.db', backup_dir='data/backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self):
        """Create a backup of the database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = os.path.basename(self.db_path).replace('.db', '')
        backup_file = os.path.join(self.backup_dir, f'{backup_name}_{timestamp}.backup.db')
        
        try:
            shutil.copy2(self.db_path, backup_file)
            return backup_file
        except Exception as e:
            raise IOError(f"Backup failed: {str(e)}")
    
    def restore(self, backup_file):
        """Restore from a backup file"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found")
        
        try:
            if os.path.exists(self.db_path):
                temp_bak = self.db_path + '.pre_restore.bak'
                shutil.copy2(self.db_path, temp_bak)
            
            shutil.copy2(backup_file, self.db_path)
        except Exception as e:
            raise IOError(f"Restore failed: {str(e)}")
    
    def auto_backup(self, keep_days=30):
        """Create automatic daily backup and clean old ones"""
        backup_file, msg = self.create_backup()
        
        if backup_file:
            # Clean old backups
            self._cleanup_old_backups(keep_days)
        
        return backup_file, msg
    
    def _cleanup_old_backups(self, keep_days):
        """Remove backups older than keep_days"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for file in os.listdir(self.backup_dir):
            if file.startswith('pos_system_backup_'):
                file_path = os.path.join(self.backup_dir, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                    except:
                        pass
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for file in sorted(os.listdir(self.backup_dir), reverse=True):
            if file.startswith('pos_system_backup_'):
                file_path = os.path.join(self.backup_dir, file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                created = datetime.fromtimestamp(os.path.getctime(file_path))
                
                backups.append({
                    'file': file,
                    'path': file_path,
                    'size': size_mb,
                    'created': created.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return backups
=======
"""
Backup and restore utilities
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    """Handle database backups and restores"""
    
    def __init__(self, db_path='data/pos_system.db', backup_dir='data/backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self):
        """Create a backup of the database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = os.path.basename(self.db_path).replace('.db', '')
        backup_file = os.path.join(self.backup_dir, f'{backup_name}_{timestamp}.backup.db')
        
        try:
            shutil.copy2(self.db_path, backup_file)
            return backup_file
        except Exception as e:
            raise IOError(f"Backup failed: {str(e)}")
    
    def restore(self, backup_file):
        """Restore from a backup file"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Backup file not found")
        
        try:
            if os.path.exists(self.db_path):
                temp_bak = self.db_path + '.pre_restore.bak'
                shutil.copy2(self.db_path, temp_bak)
            
            shutil.copy2(backup_file, self.db_path)
        except Exception as e:
            raise IOError(f"Restore failed: {str(e)}")
    
    def auto_backup(self, keep_days=30):
        """Create automatic daily backup and clean old ones"""
        backup_file, msg = self.create_backup()
        
        if backup_file:
            # Clean old backups
            self._cleanup_old_backups(keep_days)
        
        return backup_file, msg
    
    def _cleanup_old_backups(self, keep_days):
        """Remove backups older than keep_days"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        for file in os.listdir(self.backup_dir):
            if file.startswith('pos_system_backup_'):
                file_path = os.path.join(self.backup_dir, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                    except:
                        pass
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for file in sorted(os.listdir(self.backup_dir), reverse=True):
            if file.startswith('pos_system_backup_'):
                file_path = os.path.join(self.backup_dir, file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                created = datetime.fromtimestamp(os.path.getctime(file_path))
                
                backups.append({
                    'file': file,
                    'path': file_path,
                    'size': size_mb,
                    'created': created.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return backups
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
