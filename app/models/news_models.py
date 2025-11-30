from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String, nullable=False, default='unknown')
    url = Column(String, unique=True, nullable=False, index=True)
    publish_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    authors = Column(ARRAY(String), default=list)
    keywords = Column(ARRAY(String), default=list)
    summary = Column(Text)
    top_image = Column(String)
    is_processed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"