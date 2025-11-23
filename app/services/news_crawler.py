import asyncio
import aiohttp
from bs4 import BeautifulSoup
from newspaper import Article
from typing import List, Dict, Optional
import logging
from datetime import datetime
from fake_useragent import UserAgent
import json

logger = logging.getLogger(__name__)


class NewsCrawler:
    def __init__(self):
        ua = UserAgent()

        self.headers = {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive'
        }

        self.timeout = aiohttp.ClientTimeout(total=40)
        self.connector = aiohttp.TCPConnector(
            limit=10,
            ssl=False,
            ttl_dns_cache=300,
            enable_cleanup_closed=True
        )

        self.sources = [
            {
                'name': 'Yahoo Finance',
                'url': 'https://finance.yahoo.com/topic/latest-news/',
                'selectors': {
                    'articles': 'a.subtle-link',
                    'link_attr': 'href',
                    'base_url': 'https://finance.yahoo.com',
                    'max_articles': 5
                }
            },
            {
                'name': 'MarketWatch',
                'url': 'https://www.marketwatch.com/latest-news',
                'selectors': {
                    'articles': 'h3.article__headline a',
                    'link_attr': 'href',
                    'base_url': 'https://www.marketwatch.com',
                    'max_articles': 5
                }
            }
        ]

        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
            connector=self.connector,
            cookie_jar=aiohttp.DummyCookieJar()  # ✅ Prevent Yahoo cookie overflow crash
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_url(self, url: str) -> Optional[str]:
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                return await response.text()
        except Exception as e:
            logger.error(f"Fetch failed {url}: {str(e)}")
            return None

    async def extract_article_content(self, url: str) -> Optional[Dict]:
        try:
            html = await self.fetch_url(url)
            if not html:
                return None

            article = Article(url)

            # Works for both newspaper3k and newspaper4k
            if hasattr(article, "set_html"):
                article.set_html(html)
            else:
                article.download(input_html=html)

            article.parse()
            article.nlp()

            return {
                'title': article.title or "No title",
                'text': article.text,
                'summary': article.summary,
                'authors': article.authors,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'url': url,
                'keywords': article.keywords,
                'top_image': article.top_image,
                'scraped_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Article parse failed {url}: {str(e)}")
            return None

    async def crawl_source(self, source: Dict) -> List[Dict]:
        articles = []
        logger.info(f"Crawling {source['name']}...")

        html = await self.fetch_url(source['url'])
        if not html:
            logger.warning(f"No HTML from {source['name']}")
            return articles

        soup = BeautifulSoup(html, 'html.parser')
        links = soup.select(source['selectors']['articles'])
        max_articles = source['selectors']['max_articles']

        logger.info(f"Found {len(links)} links on {source['name']}")

        for i, link in enumerate(links[:max_articles]):
            href = link.get(source['selectors']['link_attr'])
            if not href:
                continue

            if not href.startswith('http'):
                href = source['selectors']['base_url'] + href

            data = await self.extract_article_content(href)
            if data:
                data['source'] = source['name']
                articles.append(data)

            await asyncio.sleep(1)  # polite delay

        logger.info(f"{source['name']} -> {len(articles)} articles extracted")
        return articles

    async def crawl_all_sources(self) -> List[Dict]:
        results = await asyncio.gather(
            *[self.crawl_source(source) for source in self.sources],
            return_exceptions=True
        )

        all_articles = []
        for r in results:
            if isinstance(r, list):
                all_articles.extend(r)

        return all_articles

    def save_to_json(self, articles: List[Dict], filename: str = 'news_articles.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(articles)} articles to {filename}")


# Standalone test
async def main():
    async with NewsCrawler() as crawler:
        articles = await crawler.crawl_all_sources()
        print(f"✅ Crawled {len(articles)} articles")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
