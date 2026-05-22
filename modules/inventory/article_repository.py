"""
Article Repository
Data access operations for articles
"""

from typing import Optional, List, Dict, Any
from repositories.base_repository import BaseRepository
from models.article import Article
from core.exceptions import NotFoundError, DuplicateError
from services.numbering_service import NumberingService


class ArticleRepository(BaseRepository):
    """Repository for article CRUD operations"""
    
    def __init__(self):
        super().__init__(table_name='erp_articles', primary_key='id')
    
    def create_article(self, article: Article) -> int:
        """Create a new article"""
        if not article.code:
            article.code = NumberingService.generate_article_code()
        
        if article.code and self._code_exists(article.code):
            raise DuplicateError(f"Article with code {article.code} already exists")
        
        data = article.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.create(data)
    
    def get_article(self, article_id: int) -> Optional[Article]:
        """Get article by ID"""
        data = self.get_by_id(article_id)
        return Article.from_dict(data) if data else None
    
    def get_article_by_code(self, code: str) -> Optional[Article]:
        """Get article by code"""
        articles = self.get_all(filters={'code': code}, limit=1)
        return Article.from_dict(articles[0]) if articles else None
    
    def get_article_by_barcode(self, barcode: str) -> Optional[Article]:
        """Get article by barcode"""
        articles = self.get_all(filters={'barcode': barcode}, limit=1)
        return Article.from_dict(articles[0]) if articles else None
    
    def get_all_articles(self, filters: Optional[Dict[str, Any]] = None,
                        order_by: str = "name ASC",
                        active_only: bool = False) -> List[Article]:
        """Get all articles"""
        if filters is None:
            filters = {}
        if active_only:
            filters['is_active'] = 1
        
        data_list = self.get_all(filters=filters, order_by=order_by)
        return [Article.from_dict(data) for data in data_list]
    
    def search_articles(self, query: str, active_only: bool = False) -> List[Article]:
        """Search articles"""
        from core.database import get_connection
        
        with get_connection() as conn:
            search_pattern = f"%{query}%"
            sql = """
                SELECT * FROM erp_articles
                WHERE (name LIKE ? OR code LIKE ? OR barcode LIKE ? OR description LIKE ?)
            """
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
            
            if active_only:
                sql += " AND is_active = 1"
            
            sql += " ORDER BY name ASC"
            
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [Article.from_dict(dict(row)) for row in rows]
    
    def get_low_stock_articles(self, depot_id: Optional[int] = None) -> List[Article]:
        """Get articles with low stock"""
        from core.database import get_connection
        
        with get_connection() as conn:
            sql = """
                SELECT * FROM erp_articles
                WHERE is_active = 1 
                AND min_stock > 0 
                AND current_stock < min_stock
            """
            params = []
            
            if depot_id:
                sql += " AND depot_id = ?"
                params.append(depot_id)
            
            sql += " ORDER BY (min_stock - current_stock) DESC"
            
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [Article.from_dict(dict(row)) for row in rows]
    
    def update_article(self, article: Article) -> bool:
        """Update article"""
        if not article.id:
            raise ValueError("Article ID is required for update")
        
        if article.code:
            existing = self.get_article_by_code(article.code)
            if existing and existing.id != article.id:
                raise DuplicateError(f"Article with code {article.code} already exists")
        
        data = article.to_dict()
        data['updated_at'] = self._get_current_timestamp()
        
        return self.update(article.id, data)
    
    def update_stock(self, article_id: int, quantity: float) -> bool:
        """Update article stock (used by stock service)"""
        article = self.get_article(article_id)
        if not article:
            raise NotFoundError(f"Article with ID {article_id} not found")
        
        article.current_stock = quantity
        return self.update_article(article)
    
    def delete_article(self, article_id: int) -> bool:
        """Delete article (soft delete)"""
        article = self.get_article(article_id)
        if not article:
            raise NotFoundError(f"Article with ID {article_id} not found")
        
        article.is_active = False
        return self.update_article(article)
    
    def _code_exists(self, code: str) -> bool:
        """Check if article code exists"""
        return self.get_article_by_code(code) is not None
    
    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
