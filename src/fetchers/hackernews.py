import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_hackernews() -> List[Dict[str, Any]]:
    """
    Fetches the top 30 stories from Hacker News and filters those with a score > 100.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    try:
        logger.info("Fetching top stories from Hacker News...")
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:30]

        results = []
        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_res = requests.get(story_url, timeout=10)
                story_res.raise_for_status()
                story = story_res.json()

                if story and story.get("score", 0) > 100:
                    results.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "Hacker News",
                        "score": story.get("score", 0),
                        "summary": "" # HN items typically don't have descriptions in the topstories feed
                    })
            except Exception as e:
                logger.warning(f"Error fetching Hacker News story {story_id}: {e}")
                continue

        logger.info(f"Successfully fetched {len(results)} stories from Hacker News.")
        return results
    except Exception as e:
        logger.error(f"Error fetching Hacker News: {e}")
        return []
