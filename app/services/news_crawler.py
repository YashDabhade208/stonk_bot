import asyncio
import aiohttp
from bs4 import BeautifulSoup
from newspaper import Article
from typing import List, Dict, Optional
import logging
from datetime import datetime
from fake_useragent import UserAgent
import re

logger = logging.getLogger(__name__)


NSE_STOCK_PATTERN = re.compile(r'\b[A-Z]{2,10}\b')


class NewsCrawler:
    def __init__(self):
        ua = UserAgent()

        self.headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-IN,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        self.timeout = aiohttp.ClientTimeout(total=40)
        self.connector = aiohttp.TCPConnector(limit=10, ssl=False)

        # ✅ INDIAN MARKET SOURCES
        self.sources = [
            {
                'name': 'Moneycontrol',
                'url': 'https://www.moneycontrol.com/news/business/stocks/',
                'selectors': {
                    'articles': 'li.clearfix a',
                    'link_attr': 'href',
                    'base_url': '',
                    'max_articles': 8
                }
            },
            {
                'name': 'Economic Times',
                'url': 'https://economictimes.indiatimes.com/markets/stocks/news',
                'selectors': {
                    'articles': 'div.eachStory h3 a',
                    'link_attr': 'href',
                    'base_url': 'https://economictimes.indiatimes.com',
                    'max_articles': 8
                }
            },
            {
                'name': 'LiveMint',
                'url': 'https://www.livemint.com/market',
                'selectors': {
                    'articles': 'h2.headline a',
                    'link_attr': 'href',
                    'base_url': '',
                    'max_articles': 6
                }
            }
        ]

        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=self.connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_url(self, url: str) -> Optional[str]:
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                return await response.text()
        except Exception as e:
            logger.error(f"Fetch failed {url}: {str(e)}")
            return None

    # ✅ STOCK SYMBOL EXTRACTION
    def extract_stocks(self, text: str) -> List[str]:
        matches = NSE_STOCK_PATTERN.findall(text.upper())
        blacklist = {'RBI', 'SEBI', 'COVID', 'GDP', 'Q1', 'Q2', 'Q3', 'Q4'}
        return list(set([m for m in matches if m not in blacklist]))

    # ✅ SIMPLE SENTIMENT ENGINE
    def analyze_sentiment(self, text: str) -> str:
        bullish = ['surge', 'profit jump', 'beats estimates', 'strong growth', 'upgrade', 'record high']
        bearish = ['fall', 'drop', 'loss', 'downgrade', 'weak outlook', 'plunge']

        text_lower = text.lower()

        if any(word in text_lower for word in bullish):
            return "Bullish"
        if any(word in text_lower for word in bearish):
            return "Bearish"
        return "Neutral"

    async def extract_article_content(self, url: str) -> Optional[Dict]:
        try:
            html = await self.fetch_url(url)
            if not html:
                return None

            article = Article(url)
            article.set_html(html)
            article.parse()
            article.nlp()

            content = article.text or ""
            sentiment = self.analyze_sentiment(content)
            stocks = self.extract_stocks(article.title + " " + content)

            return {
                'title': article.title or "No title",
                'text': content,
                'summary': article.summary,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'url': url,
                'source': "",
                'sentiment': sentiment,
                'mentioned_stocks': stocks,
                'scraped_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Article parse failed {url}: {str(e)}")
            return None

    async def crawl_source(self, source: Dict) -> List[Dict]:
        articles = []
        html = await self.fetch_url(source['url'])
        if not html:
            return articles

        soup = BeautifulSoup(html, 'html.parser')
        links = soup.select(source['selectors']['articles'])

        for link in links[:source['selectors']['max_articles']]:
            href = link.get(source['selectors']['link_attr'])
            if not href:
                continue
            if not href.startswith('http'):
                href = source['selectors']['base_url'] + href

            article = await self.extract_article_content(href)
            if article:
                article['source'] = source['name']
                articles.append(article)

            await asyncio.sleep(1)

        return articles

    async def crawl_all_sources(self) -> List[Dict]:
        results = await asyncio.gather(
            *[self.crawl_source(src) for src in self.sources],
            return_exceptions=True
        )

        all_articles = []
        for r in results:
            if isinstance(r, list):
                all_articles.extend(r)
        return all_articles
