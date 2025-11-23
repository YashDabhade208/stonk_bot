from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import logging

from ..models.news_models import NewsArticle, Base
from ..core.db_config import engine

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self, db: Session):
        self.db = db
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        Base.metadata.create_all(bind=engine)
    
    async def save_article(self, article_data: Dict) -> Optional[NewsArticle]:
        """Save a single article to the database"""
        try:
            # Check if article already exists
            existing = self.db.query(NewsArticle).filter_by(url=article_data['url']).first()
            if existing:
                return None
                
            article = NewsArticle(
                title=article_data.get('title', ''),
                content=article_data.get('text', ''),
                source=article_data.get('source', 'unknown'),
                url=article_data['url'],
                publish_date=article_data.get('publish_date'),
                authors=article_data.get('authors', []),
                keywords=article_data.get('keywords', []),
                summary=article_data.get('summary', ''),
                top_image=article_data.get('top_image')
            )
            
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            return article
            
        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"Article already exists: {article_data.get('url')}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving article: {str(e)}")
            return None
    
    async def save_articles(self, articles: List[Dict]) -> int:
        """Save multiple articles to the database"""
        saved_count = 0
        for article in articles:
            result = await self.save_article(article)
            if result:
                saved_count += 1
        return saved_count
    
    def get_recent_articles(self, limit: int = 10, days: int = 7) -> List[NewsArticle]:
        """Get recent articles from the database"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(NewsArticle)
            .filter(NewsArticle.created_at >= cutoff_date)
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )
    
    def search_articles(self, query: str, limit: int = 20) -> List[NewsArticle]:
        """Search articles by title or content"""
        return (
            self.db.query(NewsArticle)
            .filter(
                (NewsArticle.title.ilike(f'%{query}%')) |
                (NewsArticle.content.ilike(f'%{query}%'))
            )
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )
    
    def get_articles_by_source(self, source: str, limit: int = 20) -> List[NewsArticle]:
        """Get articles by source"""
        return (
            self.db.query(NewsArticle)
            .filter(NewsArticle.source.ilike(f'%{source}%'))
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )

# Example usage:
# from sqlalchemy.orm import sessionmaker
# from ..core.db_config import engine
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# db = SessionLocal()
# service = NewsService(db)
