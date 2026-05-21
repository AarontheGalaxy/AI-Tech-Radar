import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from fetchers.hackernews import fetch_hackernews
from fetchers.reddit import fetch_reddit
from fetchers.arxiv_fetcher import fetch_arxiv
from fetchers.github_trending import fetch_github_trending
from fetchers.devto import fetch_devto
from processors.summarizer import process_and_summarize
from interactive import launch_interactive

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(module)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def fetch_all() -> list:
    """
    Run all fetchers in parallel using ThreadPoolExecutor.
    
    Returns:
        list: A combined list of all items fetched from all sources.
    """
    fetchers = [
        fetch_hackernews,
        fetch_reddit,
        fetch_arxiv,
        fetch_github_trending,
        fetch_devto
    ]
    
    all_items = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_fetcher = {executor.submit(fetcher): fetcher.__name__ for fetcher in fetchers}
        for future in as_completed(future_to_fetcher):
            fetcher_name = future_to_fetcher[future]
            try:
                results = future.result()
                all_items.extend(results)
            except Exception as e:
                logger.error(f"{fetcher_name} generated an exception: {e}")
                
    return all_items

def save_report(data: dict):
    """
    Saves the output as a markdown file in the reports/ folder.
    
    Args:
        data (dict): The summarized data containing top_20 and one_liner.
    """
    os.makedirs("reports", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"reports/{date_str}_tech_radar.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# AI Tech Radar Report - {date_str}\n\n")
            f.write(f"**{data.get('one_liner', '')}**\n\n")
            f.write("## Top 20 Developments\n\n")
            
            for item in data.get("top_20", []):
                f.write(f"### {item.get('rank')}. {item.get('title')}\n")
                f.write(f"- **Category:** {item.get('category')}\n")
                f.write(f"- **Importance:** {item.get('importance')}/10\n")
                f.write(f"- **Summary:** {item.get('summary')}\n")
                f.write(f"- **Source:** [Link]({item.get('url')})\n\n")
                
        logger.info(f"Report successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")

def main():
    """Main Orchestrator."""
    start_time = time.time()
    
    load_dotenv()
    
    logger.info("Starting AI Tech Radar...")
    
    items = fetch_all()
    logger.info(f"Total items fetched across all sources: {len(items)}")
    
    if not items:
        logger.warning("No items fetched. Exiting.")
        return
        
    logger.info("Passing items to Ollama summarizer...")
    summary_data = process_and_summarize(items)
    
    save_report(summary_data)
    
    # Prompt for interactive mode
    while True:
        choice = input("\nOpen interactive mode? (y/n): ").lower().strip()
        if choice == 'y':
            launch_interactive(summary_data, items)
            break
        elif choice == 'n':
            print(f"\n{summary_data.get('one_liner', '')}")
            sure = input("Are you sure? (y/n): ").lower().strip()
            if sure == 'y':
                break
        else:
            continue
    
    end_time = time.time()
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
