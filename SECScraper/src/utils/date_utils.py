import re
from datetime import datetime
from typing import Optional

def parse_date(date_str: str) -> Optional[str]:
    """
    Convert various date string formats to standard format (MM/DD/YYYY)
    
    Supported formats:
    - MM/DD/YY
    - MM/DD/YYYY
    - Month DD, YYYY
    - Month. DD, YYYY
    - DD Month YYYY
    - DD Month. YYYY
    """
    try:
        # Clean input
        date_str = date_str.strip()
        
        # Try parsing MM/DD/YY or MM/DD/YYYY format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                # Handle two-digit year
                if len(year) == 2:
                    year = '19' + year if int(year) >= 77 else '20' + year
                # Ensure month and day are two digits
                month = month.zfill(2)
                day = day.zfill(2)
                return f"{month}/{day}/{year}"
        
        # Try parsing Month DD, YYYY or DD Month YYYY format
        month_pattern = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        # Support optional dot after month
        month_pattern_with_dot = fr"{month_pattern}\.?"
        
        # Pattern 1: Month DD, YYYY or Month. DD, YYYY
        pattern1 = fr"{month_pattern_with_dot}\s+(\d{{1,2}})(?:,|\s)\s*(\d{{4}})"
        # Pattern 2: DD Month YYYY or DD Month. YYYY
        pattern2 = fr"(\d{{1,2}})\s+{month_pattern_with_dot}\s+(\d{{4}})"
        
        match = re.search(pattern1, date_str, re.IGNORECASE)
        if match:
            month, day, year = match.groups()
        else:
            match = re.search(pattern2, date_str, re.IGNORECASE)
            if match:
                day, month, year = match.groups()
            else:
                return None
        
        # Convert month name to number
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        month_num = month_map[month[:3].lower()]
        day = day.zfill(2)
        
        # Validate if the date is valid
        try:
            datetime.strptime(f"{month_num}/{day}/{year}", "%m/%d/%Y")
        except ValueError:
            return None
            
        return f"{month_num}/{day}/{year}"
        
    except Exception as e:
        print(f"Error parsing date '{date_str}': {str(e)}")
        return None
