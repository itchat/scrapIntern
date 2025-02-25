import praw
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from config import REDDIT_LIMIT, TIME_RANGE_DAYS, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


def fetch_reddit_discussions(subreddits, search_terms, output_file):
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
    current_time = datetime.now(timezone.utc)
    time_range = current_time - timedelta(days=TIME_RANGE_DAYS)

    with open(output_file, 'w', encoding='utf-8') as file:
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            for search_term in search_terms:
                for submission in subreddit.search(search_term, limit=REDDIT_LIMIT):
                    submission_time = datetime.fromtimestamp(submission.created_utc, timezone.utc)
                    if submission_time >= time_range:
                        file.write(f"Title: {submission.title}\n")
                        file.write(f"URL: {submission.url}\n")
                        response = requests.get(submission.url, headers={'User-Agent': REDDIT_USER_AGENT})
                        soup = BeautifulSoup(response.content, 'html.parser')
                        post_content = soup.find('div', class_='_1qeIAgB0cPwnLhDF9XSiJM')
                        if post_content:
                            file.write(f"Content: {post_content.get_text()}\n")
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            comment_time = datetime.fromtimestamp(comment.created_utc, timezone.utc)
                            if comment_time >= time_range:
                                file.write(f"Comment by {comment.author} at {comment_time}:\n")
                                file.write(f"{comment.body}\n")
                                file.write("-" * 40 + "\n")
                        file.write("\n" + "-" * 80 + "\n\n")
    print(f"Discussions saved to {output_file}")
