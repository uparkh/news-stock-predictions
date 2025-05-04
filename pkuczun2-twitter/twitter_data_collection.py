# TWEEPY API only supports calls to <= 7 days in the past... oops
import tweepy
import csv
from datetime import datetime
import time

from config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

client = tweepy.Client(
    bearer_token=TWITTER_API_KEY,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
    wait_on_rate_limit=True
)

def get_monthly_tweets_2024():
    """Fetches 100 tweets/month in 2024 and returns {month: [tweet_texts]}."""
    monthly_tweets = {month: [] for month in [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]}
    
    query = "finance OR stock OR market OR investing lang:en -is:retweet"
    
    for month_num in range(1, 13):
        month_name = datetime(2024, month_num, 1).strftime('%b')  # "Jan", "Feb", etc.
        start_time = datetime(2024, month_num, 1).isoformat() + "Z"
        
        if month_num == 12:
            end_time = datetime(2025, 1, 1).isoformat() + "Z"
        else:
            end_time = datetime(2024, month_num + 1, 1).isoformat() + "Z"
        
        print(f"Fetching tweets for {month_name} 2024...")
        
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=100,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=["text"]
            )
            
            if response.data:
                monthly_tweets[month_name] = [tweet.text for tweet in response.data]
            else:
                print(f"No tweets found for {month_name}.")
        
        except Exception as e:
            print(f"Error fetching {month_name}: {e}")
    
    return monthly_tweets

def save_to_csv(monthly_tweets, filename="monthly_tweets_2024.csv"):
    """Saves {month: [texts]} to CSV with columns [month, text0]."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        for month, texts in monthly_tweets.items():
            for text in texts:
                writer.writerow([month, text])

if __name__ == "__main__":
    monthly_tweets = get_monthly_tweets_2024()
    save_to_csv(monthly_tweets)
    print("Twitter CSV saved")