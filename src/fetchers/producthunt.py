import requests
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_producthunt() -> List[Dict[str, Any]]:
    """
    Fetches today's top products from Product Hunt via their public API.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    token = os.getenv("PRODUCTHUNT_TOKEN")
    if not token or token == "your_producthunt_token":
        logger.error("Product Hunt API token missing. Please check .env file.")
        return []

    try:
        logger.info("Fetching top products from Product Hunt...")
        url = "https://api.producthunt.com/v2/api/graphql"
        
        query = """
        {
          posts(order: VOTES, first: 10) {
            edges {
              node {
                name
                tagline
                url
                votesCount
              }
            }
          }
        }
        """
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        posts = data.get("data", {}).get("posts", {}).get("edges", [])
        for edge in posts:
            node = edge.get("node", {})
            results.append({
                "title": node.get("name", ""),
                "url": node.get("url", ""),
                "source": "Product Hunt",
                "score": node.get("votesCount", 0),
                "summary": node.get("tagline", "")[:200]
            })
        
        logger.info(f"Successfully fetched {len(results)} products from Product Hunt.")
        return results
    except Exception as e:
        logger.error(f"Error fetching Product Hunt: {e}")
        return []
