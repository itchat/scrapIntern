import asyncio
import re
import pandas as pd
from crawl4ai import AsyncWebCrawler, CacheMode
from src.collectors.txt_collector import TXTCollector
import time
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean text using TXTCollector's method"""
    # Use regular expression to delete from the beginning to "Washington" after the dash
    text = re.sub(r'^.*?Washington,?\s*?D\.?C\.?,?\s*?(?:(?:Jan|Feb|Mar|Apr|Jun(?:e)?|Jul|Aug|Sep(?:t)?|Oct|Nov|Dec)\.?|(?:January|February|March|April|May|June|July|August|September|October|November|December))\s+?\d{1,2},?\s+?\d{4}\s*?[—–-]{1,2}?\s*?', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # Remove leading dashes and whitespace
    text = re.sub(r'^(?:-{1,2}|—|–)\s*', '', text).strip()

    # Process content line by line
    lines = text.splitlines()
    cleaned_lines = []
    found_separator = False

    for line in lines:
        line = line.strip()
        if not found_separator:
            # Check for separator to skip
            if line in ['#  #  #', '*  *  *', '# # #', '* * *', '###', '***']:
                found_separator = True
                continue
        if not found_separator:
            cleaned_lines.append(line)

    # Join all lines into a single string
    text = ' '.join(cleaned_lines)
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Clean lines containing ### or *** and their subsequent content
    text = re.sub(r'\s*(?:[#*](?:\s*[#*]\s*){2,}).*$', '', text, flags=re.DOTALL)
    
    return text.strip()

async def process_url(crawler: AsyncWebCrawler, url: str) -> str:
    """Process a single URL and return cleaned text"""
    try:
        result = await crawler.arun(url=url)
        raw_text = result.markdown_v2.raw_markdown
        return clean_text(raw_text)
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return ""

async def process_urls_with_rate_limit(crawler: AsyncWebCrawler, urls: List[str], batch_size: int = 5, delay: float = 1.0) -> List[str]:
    """Process URLs in batches with rate limiting"""
    results = []
    
    # Split URLs into batches
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
        
        # Create tasks for the current batch
        tasks = [process_url(crawler, url) for url in batch_urls]
        
        # Run the current batch concurrently
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        
        # Add delay between batches
        if i + batch_size < len(urls):  # If not the last batch
            print(f"Waiting {delay} seconds before next batch...")
            await asyncio.sleep(delay)
    
    return results

async def main():
    # Create TXTCollector instance for getting press releases
    collector = TXTCollector()
    
    # Get press releases for all years
    all_releases = []
    for year in range(1997, 2012):  # 1977-2001 data
        releases = collector.get_press_releases(year)
        all_releases.extend(releases)
        print(f"Collected {len(releases)} releases from year {year}")
        # Add delay for each year
        time.sleep(1)
    
    # Create DataFrame
    df = pd.DataFrame(all_releases)
    print(f"Total releases collected: {len(df)}")
    
    # Use crawl4ai to get and clean text
    async with AsyncWebCrawler(
        verbose=True,
        request_timeout=30,  # Increase timeout
        max_retries=3,       # Add retry count
    ) as crawler:
        # Get all URLs
        urls = df['URL'].dropna().tolist()
        
        # Process URLs with rate limiting
        print("Starting to process URLs with rate limiting...")
        texts = await process_urls_with_rate_limit(
            crawler=crawler,
            urls=urls,
            batch_size=100,    # Process 5 URLs per batch
            delay=10        # Delay between batches
        )
        
        # Update DataFrame
        df['Text'] = pd.Series(texts)
        
        # Save results, excluding URL column
        output_file = 'sec_press_releases_crawled.csv'
        df.drop(columns=['URL'], inplace=True)
        df.to_csv(output_file, index=False)
        print(f"Processed {len(texts)} URLs and saved results to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
