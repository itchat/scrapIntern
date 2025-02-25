import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict
from html2text import html2text
from .base_collector import BaseCollector
from ..utils.date_utils import parse_date

class HTMLCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self._processed_urls = set()

    def get_press_releases(self, year: int) -> List[Dict]:
        """Get press releases for the specified year"""
        url = f"{self.base_url}/news/press/pressarchive/{year}press.shtml"
        html = self.get_page_content(url)
        if not html:
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
                            if not href:
                                continue

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
                            
                            # Get title (use third cell if available, otherwise use link text)
                            details = ""
                            if len(cells) >= 3:
                                details = cells[2].get_text(strip=True)
                            if not details:
                                details = link.get_text(strip=True)
                            print(formatted_date)
                            if formatted_date and details:
                                press_releases.append({
                                    "Date": formatted_date,
                                    "Headlines": details,
                                    "URL": full_url,
                                })
                                processed_count += 1
                                logging.info(f"Found press release {processed_count}: {details}")

                        except Exception as e:
                            logging.error(f"Error processing row: {str(e)}")
                            continue
            
            print(len(press_releases))
            logging.info(f"Total unique press releases found: {len(press_releases)}")

        except Exception as e:
            logging.error(f"Error processing press releases: {str(e)}")

        return press_releases

    def extract_press_release_text(self, url: str) -> str:
        """Extract press release text and convert to Markdown format"""
        try:
            html = self.get_page_content(url)
            if not html:
                return ""

            soup = BeautifulSoup(html, "html.parser")
            
            # Define regex patterns
            pattern_pre = re.compile(r"<p>(.*?)</p>", re.DOTALL)
            
            # Find all matching content
            matches = pattern_pre.findall(str(soup))
            
            # Store all valid paragraphs
            paragraphs = []
            found_header = False
            
            for match in matches:
                # Process regular paragraph text
                content = match
                # Remove all HTML tags while preserving text content within tags
                content = re.sub(r'<(?:em|i)>(.*?)</(?:em|i)>', r'\1', content)  # Process em and i tags
                content = re.sub(r'<[^>]+>', '', content)  # Remove other HTML tags
                content = content.strip()
                
                if content:
                    paragraphs.append(content)
                    if not found_header:
                        found_header = True
                
                # Check if only date (em/i/b tags wrapped)
                date_only_match = re.search(r'<(?:em|i|b)>.*?</(?:em|i|b)>\s*?(?:[—–\-â]|&mdash;|&ndash;|-){0,1,2}\s*?(.*?)(?:</?p>|<br|$)', match)
                if date_only_match:
                    content = re.sub(r'<[^>]+>', '', date_only_match.group(1)).strip()
                    if content:
                        paragraphs.append(content)
                        found_header = True
                        continue
                
                # Skip agency lists
                if re.search(r"(?:Board of Governors.*?\n|Department of.*?\n|Federal.*?\n|Office of.*?\n|Securities.*?\n)+\d{4}-\d+\n?[--]", content):
                    continue
                
                # Skip navigation links
                if re.search(r'^Home\s*>\s*News', content):
                    continue
                        
                # Skip page header information
                if content.startswith(('FOR IMMEDIATE RELEASE', 'Modified:', 'Last modified:')):
                    continue
                        
                # Skip footer links
                if content.startswith(('Contact', 'Employment', 'Links', 'FOIA')):
                    continue
                
                # If header found, continue adding subsequent paragraphs
                if found_header:
                    # Skip navigation links
                    if re.search(r'^Home\s*>\s*News', content):
                        continue
                        
                    # Skip page header information
                    if content.startswith(('FOR IMMEDIATE RELEASE', 'Modified:', 'Last modified:')):
                        continue
                        
                    # Skip footer links
                    if content.startswith(('Contact', 'Employment', 'Links', 'FOIA')):
                        continue
                    
                    if content and content not in paragraphs:  # Avoid duplicate paragraphs
                        paragraphs.append(content)
            
            # Initialize full_text
            full_text = "\n\n".join(paragraphs) if paragraphs else ""
            
            # If no Washington format content found, try other extraction methods
            if not full_text.strip():
                paragraphs = []
                content_started = False
                
                for match in matches:
                    # Check if table format (What/Who/When etc.)
                    if '<table' in match and ('What:' in match or 'Who:' in match or 'When:' in match):
                        # Extract table content
                        table_items = []
                        for field in ['What:', 'Who:', 'When:', 'Where:', 'Contact:', 'Other:']:
                            field_match = re.search(rf'<td[^>]*>\s*<b[^>]*>{field}</b>\s*</td>\s*<td[^>]*>(.*?)</td>', match, re.DOTALL)
                            if field_match:
                                content = re.sub(r'<[^>]+>', '', field_match.group(1)).strip()
                                if content:
                                    table_items.append(f"{field} {content}")
                        if table_items:
                            paragraphs.extend(table_items)
                            break
                    
                    # Check if only date (em tag wrapped)
                    date_only_match = re.search(r'<(?:em|i)>.*?</(?:em|i)>\s*?(?:[—–\-â]|&mdash;|&ndash;){1,2}\s*?(.*?)(?:</?p>|<br|$)', match)
                    if date_only_match:
                        content = re.sub(r'<[^>]+>', '', date_only_match.group(1)).strip()
                        if content:
                            paragraphs.append(content)
                            found_header = True
                            continue
                    
                    # Check if only date (i tag wrapped)
                    date_only_match_i = re.search(r'<i>(?:(?:Jan|Feb|Mar|Apr|Jun(?:e)?|Jul|Aug|Sep(?:t)?|Oct|Nov|Dec)\.?|(?:January|February|March|April|May|June|July|August|September|October|November|December))\s+?\d{1,2},?\s+?\d{4}</i>\s*?(?:[—–\-â]|&mdash;|&ndash;){1,2}\s*?(.*?)(?:</?p>|<br|$)', match)
                    if date_only_match_i:
                        content = re.sub(r'<[^>]+>', '', date_only_match_i.group(1)).strip()
                        if content:
                            paragraphs.append(content)
                            found_header = True
                            continue
                    
                    # Check if only date (b tag wrapped)
                    date_only_match_b = re.search(r'<b>.*?</b>(?:[—–\-â]|&mdash;|&ndash;|-|\s)*?(The\s+Commission.*?)(?:</?p>|<br|$)', match)
                    if date_only_match_b:
                        content = re.sub(r'<[^>]+>', '', date_only_match_b.group(1)).strip()
                        if content:
                            paragraphs.append(content)
                            found_header = True
                            continue
                    
                    # Process regular paragraph text
                    content = match
                    # Remove all HTML tags while preserving text content within tags
                    content = re.sub(r'<(?:em|i)>(.*?)</(?:em|i)>', r'\1', content)  # Process em and i tags
                    content = re.sub(r'<[^>]+>', '', content)  # Remove other HTML tags
                    content = content.strip()
                    
                    # Check if contains end marker
                    if any(mark in content for mark in ["###", "# # #", "* * *", "#  #  #", "*  *  *", "***"]):
                        break
                    
                    # Skip navigation links
                    if re.search(r'^Home\s*>\s*News', content):
                        continue
                        
                    # Skip page header information
                    if content.startswith(('FOR IMMEDIATE RELEASE', 'Modified:', 'Last modified:')):
                        continue
                        
                    # Skip footer links
                    if content.startswith(('Contact', 'Employment', 'Links', 'FOIA')):
                        continue
                    
                    # If encountered h1 or h2 tag, it means the main content has started
                    if re.search(r'<h[12][^>]*>', match):
                        content_started = True
                    
                    # If content has started and is not empty, add to paragraphs
                    if content_started and content and not content.startswith((
                        "http://",
                        "Home",
                        "Previous Page",
                        "Modified:",
                        "Last modified:",
                        "Contact",
                        "Employment",
                        "Links",
                        "FOIA",
                        "Forms",
                        "Privacy"
                    )):
                        # If it's a new title (starts with uppercase letter), add two newlines
                        if re.match(r'^[A-Z]', content) and len(paragraphs) > 0:
                            paragraphs.append("")
                        paragraphs.append(content)
                
                full_text = "\n\n".join(paragraphs)
        
            
            # Initialize full_text
            full_text = "\n\n".join(paragraphs) if paragraphs else ""
            
            # Clean webpage footer navigation links and modification dates
            footer_patterns = [
                r'Home\s*\|\s*Previous Page',
                r'Modified:\s*\d{2}/\d{2}/\d{4}',
                r'Last modified:\s*\d{2}/\d{2}/\d{4}',
                r'http://www\.sec\.gov/.*?\.htm\s*$'
            ]
            
            for pattern in footer_patterns:
                full_text = re.sub(pattern, '', full_text, flags=re.IGNORECASE)
            
            # Clean standard format at the beginning of press release
            header_patterns = [
                r'FOR IMMEDIATE RELEASE\s+\d{4}-\d+',
                r'Washington,\s+D\.C\.,\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\s*(?:â|–|-|\s)*',
                r'Joint Release',
            ]
            
            for pattern in header_patterns:
                full_text = re.sub(pattern, '', full_text, flags=re.IGNORECASE)
            
            # Clean agency list and related content
            agencies_pattern = r'(?:Board of Governors.*?\n|Department of.*?\n|Federal.*?\n|Office of.*?\n)+\d{4}-\d+\n?[–-]'
            full_text = re.sub(agencies_pattern, '', full_text, flags=re.MULTILINE | re.DOTALL)
            
            # Clean content starting with dashes
            full_text = re.sub(r'^.*?[–—-]', '', full_text, flags=re.MULTILINE).strip()
            
            # Clean content after list markers
            full_text = re.sub(r'(?m)^[\s]*[#\*]+.*$', '', full_text)
            
            # Clean extra blank lines
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = full_text.strip()
            
            # Convert to Markdown format
            markdown_content = html2text(full_text, bodywidth=0)
            
            # Truncate content at end markers
            end_marks = ["###", "# # #", "* * *", "#  #  #", "*  *  *", "***"]
            for mark in end_marks:
                if mark in markdown_content:
                    markdown_content = markdown_content[:markdown_content.index(mark)]
            
            return markdown_content.strip()

        except Exception as e:
            logging.error(f"Error extracting text from {url}: {str(e)}")
            return ""