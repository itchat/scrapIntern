import requests
from config import ALPHA_VANTAGE_API_KEY


def fetch_news_sentiments(ticker, output_file):
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
    r = requests.get(url)
    data = r.json()

    formatted_data = []
    for item in data['feed']:
        for ticker_data in item['ticker_sentiment']:
            if ticker_data['ticker'] == ticker and float(ticker_data['relevance_score']) > 0.2:
                formatted_data.append({
                    'title': item['title'],
                    'url': item['url'],
                    'time_published': item['time_published'],
                    'source': item['source'],
                    'summary': item['summary'],
                    'relevance_score': ticker_data['relevance_score'],
                    'ticker_sentiment_score': ticker_data['ticker_sentiment_score'],
                    'ticker_sentiment_label': ticker_data['ticker_sentiment_label']
                })

    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in formatted_data:
            f.write(f"Title: {entry['title']}\n")
            f.write(f"URL: {entry['url']}\n")
            f.write(f"Time Published: {entry['time_published']}\n")
            f.write(f"Source: {entry['source']}\n")
            f.write(f"Summary: {entry['summary']}\n")
            f.write(f"Relevance Score: {entry['relevance_score']}\n")
            f.write(f"Sentiment Score: {entry['ticker_sentiment_score']}\n")
            f.write(f"Sentiment Label: {entry['ticker_sentiment_label']}\n")
            f.write("-" * 30 + "\n")
    print(f"News sentiments saved to {output_file}")
