import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_devto() -> List[Dict[str, Any]]:
    """
    Fetches the top articles from Dev.to API.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    try:
        logger.info("Fetching top articles from Dev.to...")
        results = []
        tags = ["ai", "machinelearning", "python", "devops"]

        for tag in tags:
            url = "https://dev.to/api/articles"
            params = {
                "top": 7,
                "per_page": 5,
                "tag": tag
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()

            for article in articles:
                results.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source": "Dev.to",
                    "score": article.get("positive_reactions_count", 0),
                    "summary": article.get("description", "")[:200]
                })

        logger.info(f"Successfully fetched {len(results)} articles from Dev.to.")
        return results
    except Exception as e:
        logger.error(f"Error fetching Dev.to: {e}")
        return []
