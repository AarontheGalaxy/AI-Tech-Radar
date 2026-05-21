import os
import json
import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher
import ollama

logger = logging.getLogger(__name__)

def similar(a: str, b: str) -> float:
    """
    Returns a similarity ratio between two strings.
    
    Args:
        a (str): First string
        b (str): Second string
        
    Returns:
        float: Similarity ratio between 0.0 and 1.0
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates items by comparing titles using simple similarity check.
    If two titles are 70%+ similar, keep only the higher-scored one.
    
    Args:
        items (List[Dict[str, Any]]): List of fetched items
        
    Returns:
        List[Dict[str, Any]]: Deduplicated list
    """
    unique_items = []
    for item in items:
        is_duplicate = False
        for i, existing in enumerate(unique_items):
            if similar(item['title'], existing['title']) >= 0.7:
                is_duplicate = True
                # Keep the one with the higher score
                if item.get('score', 0) > existing.get('score', 0):
                    unique_items[i] = item
                break
        if not is_duplicate:
            unique_items.append(item)
    return unique_items

def process_and_summarize(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Takes all fetched items, deduplicates them, and sends to Ollama in batches
    for summarization and categorization.
    
    Args:
        items (List[Dict[str, Any]]): List of fetched items
        
    Returns:
        Dict[str, Any]: Parsed JSON response containing top_20 and one_liner
    """
    logger.info("Deduplicating items...")
    unique_items = deduplicate_items(items)
    logger.info(f"Deduplicated down to {len(unique_items)} unique items.")

    if not unique_items:
        return {"top_20": [], "one_liner": "No significant tech news to report today."}

    # Send to Ollama in batches of max 10 to avoid context overflow
    batch_size = 10
    batches = [unique_items[i:i + batch_size] for i in range(0, len(unique_items), batch_size)]
    
    all_summarized_items = []
    
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    logger.info(f"Connecting to Ollama model '{model}' at {base_url}...")
    client = ollama.Client(host=base_url)

    # We will accumulate the top 5 from each batch, then do a final pass or just sort them
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1}/{len(batches)} with Ollama...")
        
        items_str = ""
        for item in batch:
            items_str += f"- Title: {item['title']}\n  URL: {item['url']}\n  Source: {item['source']}\n  Score: {item['score']}\n  Summary: {item['summary']}\n\n"

        prompt = f"""You are a tech news analyst. Below is a list of today's trending topics in AI and technology.
Your tasks:

Identify the TOP 20 most important developments
For each, write a 2-sentence summary in plain English
Assign a category: [AI/ML, DevTools, Security, Web, Systems, Research, Other]
Give an importance score from 1-10

Items:
{items_str}
Respond in this exact JSON format:
{{
"top_20": [
{{
"rank": 1,
"title": "...",
"category": "...",
"importance": 8,
"summary": "...",
"url": "..."
}}
],
"one_liner": "Today in tech: ..."
}}"""

        try:
            # We enforce JSON output format through prompt and Ollama's format feature if supported
            response = client.generate(model=model, prompt=prompt, format='json')
            content = response['response']
            
            try:
                data = json.loads(content)
                all_summarized_items.extend(data.get('top_20', []))
            except json.JSONDecodeError:
                logger.warning("JSON parsing failed. Retrying once with a simpler prompt...")
                simple_prompt = prompt + "\n\nCRITICAL: You MUST respond ONLY with valid, raw JSON. Do not include markdown formatting or explanation text."
                retry_response = client.generate(model=model, prompt=simple_prompt, format='json')
                data = json.loads(retry_response['response'])
                all_summarized_items.extend(data.get('top_20', []))
                
        except Exception as e:
            logger.error(f"Error processing batch {i+1} with Ollama: {e}")

    # If we have no items after all batches
    if not all_summarized_items:
        return {"top_20": [], "one_liner": "Ollama processing failed."}

    # Sort all gathered items by importance descending and take the absolute top 20
    all_summarized_items = [x for x in all_summarized_items if isinstance(x, dict)]
    all_summarized_items.sort(key=lambda x: x.get('importance', 0), reverse=True)
    top_20 = all_summarized_items[:20]
    
    # Re-assign ranks 1 to 20
    for idx, item in enumerate(top_20, 1):
        item['rank'] = idx

    # For the one-liner, just use the last successful response's one_liner or generate a generic one
    one_liner = "Today in tech brings major developments across AI, research, and systems."
    if 'data' in locals() and data.get('one_liner'):
        one_liner = data.get('one_liner')

    return {
        "top_20": top_20,
        "one_liner": one_liner
    }
