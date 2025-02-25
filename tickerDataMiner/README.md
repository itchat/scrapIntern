# Marketing Sentiments Data Scrapping

## Overview
This project identifies the most relevant stock ticker based on the user’s description of a company. 
It then scrapes the latest user discussions and analyses about the stock from Yahoo Finance and various major subreddits. 
Additionally, it utilizes the API of a financial machine learning platform to retrieve the latest expert news and sentiment analysis for the identified stock ticker.

## Prerequisites
- Python 3.13
- Virtual environment (venv)
- Required Python packages (listed in `requirements.txt`)

## Setup and Deployment

### 1. Create and Activate Virtual Environment
```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Run the Application
```sh 
python run.py
```

Type in the company name and the program will return the most relevant stock ticker.

```sh
Enter the stock ticker: Amazon
```

AMZN will be automatically recognized as the stock ticker for Amazon. 
Then the text data will be saved later, and you could change the scrapping settings in the `config.py` file.
