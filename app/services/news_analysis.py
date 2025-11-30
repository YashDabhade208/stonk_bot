from app.llm_client import llm

class NewsAnalysisService:

    async def analyze_news(self, article):
        prompt = f"""
        Analyze the following stock market news and provide:

        1. Very short summary (max 40 words)
        2. Sentiment score (-1 to 1)
        3. Impact rating on stock market (1–5)
        4. Key risk or opportunity described

        News:
        Title: {article['title']}
        Content: {article['content']}
        """

        response = llm(prompt)

        return response
