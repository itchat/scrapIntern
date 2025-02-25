# Summer Intern - SEC Press Release Scraper

A Python web scraper for collecting and extracting press releases from the U.S. Securities and Exchange Commission (SEC). This project can collect all press releases from 1977 to 2011 and save them in a structured CSV format.

## Project Structure

```
SEC_Scraper/
├── src/
│   ├── collectors/        # Press release collectors
│   │   ├── base_collector.py
│   │   ├── html_collector.py
│   │   └── txt_collector.py
│   ├── parsers/           # Parsers
│   │   ├── html_parser.py
│   │   └── txt_parser.py
│   └── utils/             # Utility functions
│       └── date_utils.py
├── main.py                # Main program
├── main_crawl4ai.py       # An experimental crawling way by using crawl4ai
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

## Features

- Supports two formats of press release collection:
  - HTML format (2002-2011)
  - TXT format (1977-2001)
- Automatic handling of different date formats
- Intelligent extraction of press release text, removing irrelevant content
- Results sorted by date in ascending order
- Complete logging
- Graceful error handling

## Installation

1. Clone the repository:
```bash
# Upload Later
git clone https://github.com/itchat/SEC_Scraper.git
cd SEC_Scraper
```

2. Create and activate a virtual environment:

For macOS/Linux:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

For Windows:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your virtual environment is activated (you should see (.venv) in your terminal prompt)

2. Run the scraper:
```bash
python main.py
```

3. To deactivate the virtual environment when you're done:
```bash
deactivate
```

## Output Format

The scraper generates a file named `sec_press_releases.csv` with the following columns:
- Date: Press release publication date (format: MM/DD/YYYY)
- Headlines: Press release title
- Text: Press release content

## Important Notes

- Please comply with SEC website's terms of use
- It's recommended to set appropriate request intervals to avoid server strain
- Ensure a stable internet connection
- Always run the scraper within the virtual environment

## License

MIT License
