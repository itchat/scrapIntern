import logging
import pandas as pd
from typing import List, Dict
from src.collectors.html_collector import HTMLCollector
from src.collectors.txt_collector import TXTCollector
import os

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )

def collect_press_releases(start_year: int, end_year: int, max_retries: int = 3) -> List[Dict]:
    """Collect all press releases within the specified year range"""
    all_releases = []
    failed_items = []
    
    # Initialize collectors
    html_collector = HTMLCollector()
    txt_collector = TXTCollector()
    
    for year in range(start_year, end_year + 1):
        logging.info(f"Processing year {year}")
        
        # Get all press releases for this year (with retry)
        releases = None
        retry_count = 0
        
        # Choose the correct collector based on year
        collector = txt_collector if 1997 <= year <= 2001 else html_collector
        while releases is None and retry_count < max_retries:
            try:
                releases = collector.get_press_releases(year)
                if not releases:
                    raise Exception("No releases found")
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logging.warning(f"Retry {retry_count}/{max_retries} getting releases for year {year}: {str(e)}")
                    releases = None
                else:
                    logging.error(f"Failed to get releases for year {year} after {max_retries} retries")
                    continue
        
        if not releases:
            logging.warning(f"No releases found for year {year}")
            continue
        logging.info(f"Found {len(releases)} releases for year {year}")
        
        # Extract text from each press release (with retry)
        year_releases = []
        for i, release in enumerate(releases, 1):
            retry_count = 0
            success = False
            
            while not success and retry_count < max_retries:
                try:
                    # Choose appropriate collector based on URL extension
                    url = release["URL"].lower()
                    collector = html_collector if url.endswith('.htm') or url.endswith('.html') else txt_collector
                    
                    text = collector.extract_press_release_text(release["URL"])
                    if not text:
                        raise Exception("Empty text returned")
                    
                    # Validate text content
                    if len(text.strip()) < 20:  # Ensure text length is reasonable
                        raise Exception("Text too short")
                    
                    release["Text"] = text
                    year_releases.append(release)
                    success = True
                    logging.info(f"Successfully processed release {i}/{len(releases)} for year {year}")
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logging.warning(f"Retry {retry_count}/{max_retries} for year {year} release {i}: {str(e)}")
                    else:
                        logging.error(f"Failed to collect year {year} release {i} after {max_retries} retries")
                        # Add to yearly list even if extraction failed, but with empty text
                        release["Text"] = ""
                        year_releases.append(release)
                        failed_items.append({
                            "year": year,
                            "index": i,
                            "url": release["URL"],
                            "error": str(e)
                        })
        
        # Check completeness of year data
        if len(year_releases) < len(releases) * 0.8:  # If success rate is below 80%
            logging.error(f"Year {year} data might be incomplete. Only got {len(year_releases)}/{len(releases)} releases")
            continue
        
        all_releases.extend(year_releases)
        logging.info(f"Successfully collected {len(year_releases)} releases for year {year}")
    
    # Final completeness check
    if not all_releases:
        logging.error("No releases were collected!")
        return []
        
    if failed_items:
        logging.warning(f"Failed to collect {len(failed_items)} items")
        # Save failed items to file
        df = pd.DataFrame(failed_items)
        df.to_csv('failed_items.csv', index=False)
        
    return all_releases

def save_to_csv(releases: List[Dict], output_file: str):
    """Save press releases to CSV file"""
    if not releases:
        logging.warning("No press releases to save")
        return
        
    # Create DataFrame
    df = pd.DataFrame(releases)
    
    # Data validation
    required_columns = ["Date", "Headlines", "Text"]
    for col in required_columns:
        if col not in df.columns:
            logging.error(f"Missing required column: {col}")
            return
    
    # Filter out invalid text data
    df = df[~df["Text"].str.contains(r"DOCTYPE html", na=False, case=False)]

    # Ensure Date column is in datetime format
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Convert invalid dates to NaT
    except Exception as e:
        logging.error(f"Error converting 'Date' column to datetime: {str(e)}")
        return
    
    # Verify data integrity
    empty_dates = df[df["Date"].isna()].index
    empty_headlines = df[df["Headlines"].isna()].index
    empty_texts = df[df["Text"].isna()].index
    
    if len(empty_dates) > 0:
        logging.error(f"Found {len(empty_dates)} entries with empty dates")
    if len(empty_headlines) > 0:
        logging.error(f"Found {len(empty_headlines)} entries with empty headlines")
    if len(empty_texts) > 0:
        logging.error(f"Found {len(empty_texts)} entries with empty texts")
    
    # Check for records with too short text
    short_texts = df[df["Text"].str.len() < 20]
    if not short_texts.empty:
        logging.warning(f"Found {len(short_texts)} entries with text length < 20 characters")
        # Save to failed_items.csv
        failed_items = []
        for _, row in short_texts.iterrows():
            failed_items.append({
                "year": row["Date"].year,
                "index": row.name,
                "url": row["URL"],
                "error": "Text too short (< 20 characters)"
            })
        # Append if file exists, create new file if it doesn't
        failed_df = pd.DataFrame(failed_items)
        if os.path.exists('failed_items.csv'):
            failed_df.to_csv('failed_items.csv', mode='a', header=False, index=False)
        else:
            failed_df.to_csv('failed_items.csv', index=False)
    
    # Keep only complete data
    df = df.dropna(subset=required_columns)
    
    # Sort by date in descending order
    df = df[required_columns]
    df = df.sort_values("Date", ascending=False)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    logging.info(f"Saved {len(df)} press releases to {output_file}")

def main():
    """Main function"""
    setup_logging()
    
    # Collect press releases from 1997-2011
    releases = collect_press_releases(1997, 2011)
    
    # Save results
    save_to_csv(releases, "sec_press_releases.csv")

if __name__ == "__main__":
    main()
