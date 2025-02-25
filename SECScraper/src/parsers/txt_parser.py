import re
from typing import Optional, Dict

class TXTParser:
    @staticmethod
    def parse_press_release(content: str) -> Optional[Dict[str, str]]:
        """Parse TXT formatted press release"""
        try:
            # Get title (usually at the beginning of the file)
            lines = content.split('\n')
            title = ""
            for line in lines:
                if line.strip() and not line.startswith(('FOR IMMEDIATE RELEASE', 'http://', 'Modified:')):
                    title = line.strip()
                    break
            
            # Get date
            date = ""
            date_pattern = r"\d{1,2}/\d{1,2}/\d{4}"
            date_match = re.search(date_pattern, content)
            if date_match:
                date = date_match.group(0)
            
            return {
                "title": title,
                "date": date,
            }
            
        except Exception as e:
            print(f"Error parsing TXT: {str(e)}")
            return None
