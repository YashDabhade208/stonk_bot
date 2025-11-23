from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
from fastapi.responses import JSONResponse

from app.services.news_crawler import NewsCrawler
from app.services.news_service import NewsService
from app.models.schemas import NewsArticleResponse, NewsArticleCreate
from app.core.db_config import get_db, test_db_connection

router = APIRouter()




# Initialize logger
logger = logging.getLogger(__name__)



@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Check the status of the news service"""
    try:
        db_ok = test_db_connection()
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if db_ok else "disconnected",
            "sources": ["Yahoo Finance", "MarketWatch"],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

@router.get("/crawl", response_model=List[NewsArticleResponse])
async def crawl_news(
    limit: int = 10,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    """
    Crawl news from configured sources and optionally save to database
    
    - **limit**: Maximum number of articles to return (default: 10)
    - **save_to_db**: Whether to save articles to the database (default: True)
    """
    try:
        news_service = NewsService(db)
        
        # Log the start of crawling
        logger.info(f"Starting news crawl (limit: {limit}, save_to_db: {save_to_db})")
        
        async with NewsCrawler() as crawler:
            # Add timeout to prevent hanging
            articles = await asyncio.wait_for(
                crawler.crawl_all_sources(),
                timeout=300  # 5 minutes timeout
            )
            
            if not articles:
                logger.warning("No articles were found during crawling")
                return []
                
            logger.info(f"Crawled {len(articles)} articles")
            
            if save_to_db:
                try:
                    saved_articles = await news_service.save_articles(articles)
                    logger.info(f"Successfully saved {len(saved_articles)} articles to database")
                    
                    # Return the saved articles from database to ensure consistency
                    recent_articles = news_service.get_recent_articles(limit=limit)
                    return [article.to_dict() for article in recent_articles]
                    
                except Exception as save_error:
                    logger.error(f"Error saving articles to database: {str(save_error)}", exc_info=True)
                    # If saving fails, still return the crawled articles without saving
                    if not save_to_db:
                        raise
            
            return [{
                'title': a.get('title', 'No title'),
                'source': a.get('source', 'Unknown'),
                'url': a.get('url', '#'),
                'publish_date': a.get('publish_date', datetime.utcnow().isoformat()),
                'summary': a.get('summary', '')
            } for a in articles[:limit]]
            
    except asyncio.TimeoutError:
        logger.error("News crawling timed out after 5 minutes")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="News crawling operation timed out"
        )
    except Exception as e:
        logger.error(f"Error in crawl_news: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error crawling news: {str(e)}"
        )

@router.get("/recent", response_model=List[NewsArticleResponse])
def get_recent_news(
    limit: int = 10,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get recent news articles from the database
    """
    try:
        news_service = NewsService(db)
        articles = news_service.get_recent_articles(limit=limit, days=days)
        return [article.to_dict() for article in articles]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recent news: {str(e)}"
        )

@router.get("/search", response_model=List[NewsArticleResponse])
def search_news(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search news articles by query
    """
    try:
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Search query must be at least 2 characters long"
            )
            
        news_service = NewsService(db)
        articles = news_service.search_articles(query, limit=limit)
        return [article.to_dict() for article in articles]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching news: {str(e)}"
        )

@router.get("/sources/{source}", response_model=List[NewsArticleResponse])
def get_news_by_source(
    source: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get news articles by source
    """
    try:
        news_service = NewsService(db)
        articles = news_service.get_articles_by_source(source, limit=limit)
        return [article.to_dict() for article in articles]
    except Exception as e:
      
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching news by source: {str(e)}"
        )