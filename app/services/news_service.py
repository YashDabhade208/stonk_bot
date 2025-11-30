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
        logger.info("🟢 Initializing NewsService...")
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        logger.info("📦 Checking / Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Table check complete")

    async def save_article(self, article_data: Dict) -> Optional[NewsArticle]:
        """Save a single article to the database"""
        logger.info(f"➡️ Attempting to save article: {article_data.get('title')}")

        try:
            url = article_data.get('url')
            if not url:
                logger.warning("⚠️ Article skipped - missing URL")
                return None

            existing = self.db.query(NewsArticle).filter_by(url=url).first()
            if existing:
                logger.info(f"⏩ Duplicate found, skipping: {url}")
                return None

            article = NewsArticle(
                title=article_data.get('title', ''),
                content=article_data.get('text', ''),
                source=article_data.get('source', 'unknown'),
                url=url,
                publish_date=article_data.get('publish_date'),
                authors=article_data.get('authors', []),
                keywords=article_data.get('keywords', []),
                summary=article_data.get('summary', ''),
                top_image=article_data.get('top_image'),
                created_at=datetime.utcnow()
            )

            logger.debug(f"📝 Prepared model: {article.title}")

            self.db.add(article)
            logger.info("✅ Added article to DB session")

            self.db.commit()
            logger.info("💾 Commit successful")

            self.db.refresh(article)
            logger.info(f"🎉 Article saved with ID: {article.id}")

            return article

        except IntegrityError as e:
            self.db.rollback()
            logger.warning(f"⚠️ IntegrityError - likely duplicate: {article_data.get('url')}")
            return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"🔥 Error saving article: {str(e)}", exc_info=True)
            return None

    async def save_articles(self, articles: List[Dict]) -> int:
        """Save multiple articles to the database"""
        logger.info(f"📥 save_articles called with {len(articles)} articles")

        saved_count = 0
        for index, article in enumerate(articles, start=1):
            logger.info(f"🔄 Processing article {index}/{len(articles)}")
            result = await self.save_article(article)
            if result:
                saved_count += 1
                logger.info(f"✅ Saved ({saved_count}) so far")
            else:
                logger.info("❌ Article not saved (duplicate or error)")

        logger.info(f"🏁 Finished saving. Total saved: {saved_count}")
        return saved_count

    def get_recent_articles(self, limit: int = 10, days: int = 7) -> List[NewsArticle]:
        logger.info(f"📊 Fetching recent articles (limit={limit}, days={days})")

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        articles = (
            self.db.query(NewsArticle)
            .filter(NewsArticle.created_at >= cutoff_date)
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"📦 Retrieved {len(articles)} recent articles from DB")
        return articles

    def search_articles(self, query: str, limit: int = 20) -> List[NewsArticle]:
        logger.info(f"🔍 Searching articles for query: {query}")

        results = (
            self.db.query(NewsArticle)
            .filter(
                (NewsArticle.title.ilike(f'%{query}%')) |
                (NewsArticle.content.ilike(f'%{query}%'))
            )
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"📄 Found {len(results)} matching articles")
        return results

    def get_articles_by_source(self, source: str, limit: int = 20) -> List[NewsArticle]:
        logger.info(f"🏷️ Fetching articles by source: {source}")

        results = (
            self.db.query(NewsArticle)
            .filter(NewsArticle.source.ilike(f'%{source}%'))
            .order_by(NewsArticle.publish_date.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"📦 Returned {len(results)} articles for source={source}")
        return results
