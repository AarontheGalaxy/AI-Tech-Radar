import arxiv
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

def fetch_arxiv() -> List[Dict[str, Any]]:
    """
    Searches Arxiv for the latest papers on specific queries from the last 7 days.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing title, url, source, score, and summary.
    """
    try:
        logger.info("Fetching latest papers from Arxiv...")
        queries = ["large language models", "AI agents", "machine learning"]
        query_str = " OR ".join(f'all:"{q}"' for q in queries)
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=query_str,
            max_results=50,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        results = []
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        for result in client.results(search):
            if result.published >= seven_days_ago:
                summary = result.summary.replace("\n", " ")[:200]
                results.append({
                    "title": result.title,
                    "url": result.entry_id,
                    "source": "Arxiv",
                    "score": 0,
                    "summary": summary
                })
            
            if len(results) >= 10:
                break
                
        logger.info(f"Successfully fetched {len(results)} papers from Arxiv.")
        return results
    except Exception as e:
        logger.error(f"Error fetching Arxiv: {e}")
        return []
