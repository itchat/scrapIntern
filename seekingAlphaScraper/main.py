import http.client
import json
import os
from dotenv import load_dotenv
import html2text
from datetime import datetime

# Load API key from environment variable
load_dotenv()
api_key = os.getenv('RAPIDAPI_KEY')

conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")

headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
}

transcript_id = "4740729"  # Replace with the actual transcript ID
try:
    conn.request("GET", f"/transcripts/v2/get-details?id={transcript_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    # Parse JSON response
    json_data = json.loads(data.decode('utf-8'))
    html_content = json_data['data']['attributes']['content']
    
    # Convert HTML to Markdown Format
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # Disable line wrapping
    markdown_content = h.handle(html_content)
    
    # Generate filename with transcript ID
    filename = f"transcript_{transcript_id}.txt"
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Transcript has been saved to {filename}")
        
except Exception as e:
    print(f"Error occurred: {str(e)}")
finally:
    conn.close()