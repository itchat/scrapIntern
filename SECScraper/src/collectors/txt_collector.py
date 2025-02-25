import re
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from .base_collector import BaseCollector
from ..utils.date_utils import parse_date

class TXTCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self._processed_urls = set()

    def get_press_releases(self, year: int) -> List[Dict]:
        """Get press releases from 1977-2001"""
        url = f"{self.base_url}/news/press/pressarchive/{year}press.shtml"
        html = self.get_page_content(url)
        if not html:
            logging.warning(f"No HTML content found for year {year}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        press_releases = []
        processed_count = 0

        try:
            # Find tables containing press releases
            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        try:
                            # Get press release link
                            link = cells[0].find("a")
                            if not link:
                                continue

                            href = link.get("href", "")
                            full_url = (
                                self.base_url + href
                                if href.startswith("/")
                                else href
                            )

                            # Check if URL has been processed
                            if full_url in self._processed_urls:
                                continue
                            self._processed_urls.add(full_url)

                            # Get date and details
                            date_text = cells[1].get_text(strip=True)
                            formatted_date = parse_date(date_text)
                            details = cells[2].get_text(strip=True)

                            if formatted_date and details:
                                press_releases.append({
                                    "Date": formatted_date,
                                    "Headlines": details,
                                    "URL": full_url,
                                })
                                processed_count += 1

                        except Exception as e:
                            logging.error(f"Error processing row: {str(e)}")
                            continue

        except Exception as e:
            logging.error(f"Error processing press releases: {str(e)}")

        logging.info(f"Total press releases collected for {year}: {len(press_releases)}")
        return press_releases

    def extract_press_release_text(self, url: str) -> str:
        """Extract the main content from SEC releases in TXT format."""
        try:
            content = self.get_page_content(url)
            if not content:
                return ""

            # Use regular expression to delete from the beginning to "Washington" and the following dash
            content = re.sub(r'^.*?Washington,?\s*?D\.?C\.?,?\s*?(?:(?:Jan|Feb|Mar|Apr|Jun(?:e)?|Jul|Aug|Sep(?:t)?|Oct|Nov|Dec)\.?|(?:January|February|March|April|May|June|July|August|September|October|November|December))\s+?\d{1,2},?\s+?\d{4}\s*?[—–-]{1,2}?\s*?', '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            
            # Remove leading dashes and whitespace
            content = re.sub(r'^(?:-{1,2}|—|–)\s*', '', content).strip()

            # Process remaining content line by line
            lines = content.splitlines()
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
            
            # Clean lines containing ### or *** and their following content
            text = re.sub(r'\s*(?:[#*](?:\s*[#*]\s*){2,}).*$', '', text, flags=re.DOTALL)

            return text.strip()

        except Exception as e:
            logging.error(f"Error extracting press release text from {url}: {str(e)}")
            return ""
