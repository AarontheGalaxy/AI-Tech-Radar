import os
import praw
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def fetch_reddit() -> List[Dict[str, Any]]:
    """
    Fetches the top 20 posts from specific subreddits over the last day.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not client_id or not client_secret or client_id == "your_reddit_client_id":
        logger.error("Reddit API credentials missing or invalid. Please check .env file.")
        return []

    try:
        logger.info("Fetching top posts from Reddit...")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        subreddits = ["MachineLearning", "artificial", "programming", "technology"]
        subreddit_str = "+".join(subreddits)
        
        results = []
        # Fetching top 20 posts from the combined subreddits
        for submission in reddit.subreddit(subreddit_str).top("day", limit=20):
            summary = submission.selftext[:200] if submission.selftext else ""
            summary = summary.replace('\n', ' ')
            results.append({
                "title": submission.title,
                "url": f"https://reddit.com{submission.permalink}",
                "source": f"Reddit (r/{submission.subreddit.display_name})",
                "score": submission.score,
                "summary": summary
            })
        
        logger.info(f"Successfully fetched {len(results)} posts from Reddit.")
        return results
    except Exception as e:
        logger.error(f"Error fetching Reddit: {e}")
        return []
