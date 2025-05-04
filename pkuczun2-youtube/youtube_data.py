import csv
from datetime import datetime
from googleapiclient.discovery import build  # pip install google-api-python-client

from config import YOUTUBE_API_KEY
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Economic news channels {Channel Name: Channel ID}
ECONOMIC_CHANNELS = {
    "CNBC": "UCvJJ_dzjViJCoLf5uKUTwoA",
    "Bloomberg": "UCUMZ7gohGI9HcU9VNsr2FJQ",
    "Financial Times": "UC2IfvC9g0E7eN8jY9tQq5mA",
    "Reuters": "UCVJG5C6g0zfoX0G3jh6wpIQ",
    "Wall Street Journal": "UCK7tptUDHh-RYDsdxO1-5QQ"
}

FINANCE_KEYWORDS = [
    "stock", "market", "invest", "economy", "fed", "sp500", "nasdaq",
    "earnings", "bull", "bear", "crypto", "bitcoin", "etf", "interest rates"
]

def clean_comment(text):
    return " ".join(text.replace("\n", " ").strip().split())

def is_finance_related(text):
    text_lower = clean_comment(text).lower()
    return any(keyword in text_lower for keyword in FINANCE_KEYWORDS)

def get_channel_videos(channel_id, start_time, end_time):
    try:
        search_response = youtube.search().list(
            channelId=channel_id,
            part="id",
            type="video",
            publishedAfter=start_time,
            publishedBefore=end_time,
            maxResults=5,
            order="date",
            relevanceLanguage="en"
        ).execute()
        return [item["id"]["videoId"] for item in search_response.get("items", [])]
    except Exception as e:
        print(f"Error")
        return []

def get_relevant_comments(video_id, max_comments=50):
    try:
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments,
            order="relevance",
            textFormat="plainText"
        )
        response = comments_request.execute()
        
        clean_comments = []
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            if is_finance_related(comment):
                clean_comments.append(clean_comment(comment))
        
        return clean_comments
    except Exception as e:
        print(f"Error")
        return []

def save_to_csv(monthly_comments, filename="economic_comments_2024.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["month", "channel", "comment"])
        for month, data in monthly_comments.items():
            for channel, comments in data.items():
                for comment in comments:
                    writer.writerow([month, channel, comment])

if __name__ == "__main__":
    monthly_comments = {}
    
    for month_num in range(1, 13):

        month_name = datetime(2024,month_num, 1).strftime('%b')
        start_time = datetime(2024, month_num, 1).isoformat() +"Z"
        end_time = datetime(2024, month_num +1, 1).isoformat() + "Z" if month_num <12 else datetime(2025,1,1).isoformat() + "Z"
        
        monthly_comments[month_name] = {}
        print(f"\n== {month_name} 2024 ==")
        
        for channel_name, channel_id in ECONOMIC_CHANNELS.items():
            video_ids = get_channel_videos(channel_id, start_time, end_time)
            monthly_comments[month_name][channel_name] = []
            
            for video_id in video_ids:
                comments = get_relevant_comments(video_id)
                monthly_comments[month_name][channel_name].extend(comments)
                print(f"  - {channel_name}: Added {len(comments)} comments (video: {video_id})")
    
    save_to_csv(monthly_comments)
