# run.py
import requests
from config import ALPHA_VANTAGE_API_KEY
from src.reddit_scraper import fetch_reddit_discussions
from src.alpha_vantage import fetch_news_sentiments
from src.yahoo_scraper import fetch_yahoo_comments


def validate_ticker(ticker):
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()
    if 'bestMatches' in data and data['bestMatches']:
        print(data['bestMatches'][0]['1. symbol'])
        return data['bestMatches'][0]['1. symbol']
    else:
        raise ValueError("Invalid ticker symbol")


def main():
    ticker = input("Enter the stock ticker: ")
    try:
        valid_ticker = validate_ticker(ticker)
    except ValueError as e:
        print(e)
        return

    subreddits = ['stocks', 'investing', 'wallstreetbets', 'ValueInvesting']
    search_terms = [valid_ticker]
    reddit_output_file = 'reddit_discussions.txt'
    news_output_file = 'marketing_sentiments.txt'
    yahoo_output_file = 'yahoo_comments.txt'

    fetch_reddit_discussions(subreddits, search_terms, reddit_output_file)
    fetch_news_sentiments(valid_ticker, news_output_file)
    fetch_yahoo_comments(valid_ticker, yahoo_output_file)


if __name__ == "__main__":
    main()
