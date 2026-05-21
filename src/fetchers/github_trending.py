import feedparser
import requests
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_github_trending() -> List[Dict[str, Any]]:
    """
    Fetches the top trending repositories for the 'daily' period from GitHub.
    Uses the GitHub search API as a robust fallback since github.com/trending doesn't officially provide an RSS feed.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    results = []
    
    try:
        logger.info("Attempting to parse GitHub Trending using feedparser...")
        # Since github.com/trending has no RSS, we'll try a common approach with feedparser
        # and if it fails to find entries (which it will on raw HTML), we fall back.
        feed_url = "https://github.com/trending"
        parsed_feed = feedparser.parse(feed_url)
        
        if parsed_feed.entries:
            for entry in parsed_feed.entries[:10]:
                results.append({
                    "title": entry.title,
                    "url": entry.link,
                    "source": "GitHub Trending",
                    "score": 0,
                    "summary": entry.summary[:200] if hasattr(entry, 'summary') else ""
                })
            logger.info(f"Successfully fetched {len(results)} trending repos via feedparser.")
            return results

        # Fallback to GitHub API (Searching for repos created in the last few days sorted by stars)
        logger.info("Feedparser returned empty, falling back to GitHub Search API for trending repos...")
        yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        api_url = f"https://api.github.com/search/repositories?q=created:>{yesterday}&sort=stars&order=desc"
        
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        
        items = res.json().get('items', [])[:10]
        for item in items:
            desc = item.get('description') or ''
            results.append({
                "title": item.get('full_name', ''),
                "url": item.get('html_url', ''),
                "source": "GitHub Trending",
                "score": item.get('stargazers_count', 0),
                "summary": str(desc)[:200]
            })
            
        logger.info(f"Successfully fetched {len(results)} trending repos via GitHub API fallback.")
        return results

    except Exception as e:
        logger.error(f"Error fetching GitHub Trending: {e}")
        return []
