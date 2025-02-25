# yahoo_scraper.py
from yahoofinancials import YahooFinancials
import http.client
import json
import time
from config import YAHOO_MAX_COMMENTS, YAHOO_API_KEY


def fetch_yahoo_comments(ticker, output_file):
    yahoo_financials = YahooFinancials(ticker)
    stock_data = yahoo_financials.get_stock_quote_type_data()
    message_board_id = stock_data[ticker]['messageBoardId']

    conn = http.client.HTTPSConnection("yh-finance.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': YAHOO_API_KEY,
        'x-rapidapi-host': "yh-finance.p.rapidapi.com"
    }

    offset = 0
    all_comments = []
    count_per_page = 100
    total_fetched = 0
    while True:
        url = f"/conversations/v2/list?messageBoardId={message_board_id}&offset={offset}&sort_by=newest&count={count_per_page}"
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()

        try:
            json_data = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            print("Error: Could not decode JSON response.")
            break

        if 'conversation' not in json_data or 'comments' not in json_data['conversation']:
            print('Error: conversation or comments not in the response, maybe the API is down')
            break

        comments_this_page = json_data['conversation']['comments']
        total_fetched += len(comments_this_page)
        all_comments.extend(comments_this_page)

        if not json_data['conversation']['has_next'] or total_fetched >= YAHOO_MAX_COMMENTS:
            break

        offset += count_per_page

    with open(output_file, 'w', encoding='utf-8') as f:
        for comment in all_comments:
            user_id = comment.get('user_id', 'Unknown User')
            timestamp = comment.get('written_at', 0)
            user_display_name = comment.get("user_display_name", "")
            if user_id in json_data['conversation']['users']:
                username = json_data['conversation']['users'][user_id].get('display_name', 'Unknown User')
            else:
                username = "Unknown User"

            if timestamp:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            else:
                time_str = "Unknown Time"

            text_content = ""
            if 'content' in comment:
                for content_item in comment['content']:
                    if content_item.get('type') == 'text':
                        text_content += content_item.get('text', '')

            if 'replies' in comment and comment['replies']:
                for reply in comment['replies']:
                    user_id = reply.get('user_id', 'Unknown User')
                    timestamp = reply.get('written_at', 0)
                    user_display_name = reply.get("user_display_name", "")
                    if user_id in json_data['conversation']['users']:
                        username_reply = json_data['conversation']['users'][user_id].get('display_name', 'Unknown User')
                        if not user_display_name:
                            user_display_name = username_reply
                    else:
                        username_reply = 'Unknown User'

                    if timestamp:
                        time_str_reply = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
                    else:
                        time_str_reply = "Unknown Time"
                    reply_text = ""
                    if 'content' in reply:
                        for content_item in reply['content']:
                            if content_item.get('type') == 'text':
                                reply_text += content_item.get('text', '')
                    f.write(f"{username_reply} ({time_str_reply}): {reply_text}\n")

            if text_content:
                f.write(f"{username} ({time_str}): {text_content}\n")
    print(f"Comments saved to {output_file}")
