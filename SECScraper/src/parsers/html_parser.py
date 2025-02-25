from bs4 import BeautifulSoup
import re
from typing import Optional, Dict

class HTMLParser:
    @staticmethod
    def parse_press_release(html: str) -> Optional[Dict[str, str]]:
        """Parse HTML formatted press release"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Get title
            title = ""
            h1_tag = soup.find("h1")
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            
            # Get date
            date = ""
            date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"
            date_match = re.search(date_pattern, html)
            if date_match:
                date = date_match.group(0)
            
            return {
                "title": title,
                "date": date,
            }
            
        except Exception as e:
            print(f"Error parsing HTML: {str(e)}")
            return None
