from abc import ABC, abstractmethod
import requests
import time
import logging
from typing import List, Dict

class BaseCollector(ABC):
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            "User-Agent": "Your Name yourname@email.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "www.sec.gov",
        }
        self.rate_limit_sleep = 0.5  # Increase delay time
        self.max_retries = 3  # Add retry count

    def get_page_content(self, url: str) -> str:
        """Get page content with retry mechanism"""
        logging.info(f"Fetching URL: {url}")
        
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.rate_limit_sleep)
                response = requests.get(url, headers=self.headers, timeout=30)  # Add timeout setting
                response.raise_for_status()
                
                # Check content length
                content = response.text
                if len(content) < 100:  # If content is too short, it might not be fully loaded
                    logging.warning(f"Content too short ({len(content)} bytes) on attempt {attempt + 1}, retrying...")
                    continue
                print(len(content))
                return content
                
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Incremental wait time
                    logging.warning(f"Error fetching {url} on attempt {attempt + 1}: {str(e)}")
                    logging.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed to fetch {url} after {self.max_retries} attempts: {str(e)}")
                    return ""
                    
        return ""

    @abstractmethod
    def get_press_releases(self, year: int) -> List[Dict]:
        """Get press releases for the specified year"""
        pass

    @abstractmethod
    def extract_press_release_text(self, url: str) -> str:
        """Extract press release text"""
        pass
