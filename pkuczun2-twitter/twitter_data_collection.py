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

def get_tweets_with_retry(query, max_results=100, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "entities", "lang"],
                user_fields=["username", "verified", "public_metrics"],
                expansions="author_id"
            )
            
            return response
        except tweepy.TooManyRequests as e:
            print(retries)
            wait_time = 20 * (2 ** retries)
            retries += 1
            print(f"Rate limited. Waiting {wait_time} seconds before retry {retries}/{max_retries}")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")

try:
    # Get tweets with retry logic
    response = get_tweets_with_retry(
        "finance OR stock OR market OR investing lang:en", 
        max_results=100
    )
    
    # Process response and save to CSV (your existing code)
    if not response or not response.data:
        print("No tweets found.")
        exit()

    tweets = response.data
    users = {u.id: u for u in (response.includes or {}).get('users', [])}
    

    # CSV file path
    csv_file_path = "finance_tweets.csv"

    # Write to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Header row
        csv_writer.writerow([
            'Tweet_ID',
            'Created_At',
            'Text',
            'Username',
            'User_Followers',
            'Retweet_Count',
            'Like_Count',
            'Language',
            'Hashtags',
            'User_Verified'
        ])
        
        for tweet in tweets:
            user = users[tweet.author_id]
            hashtags = ', '.join([h['tag'] for h in (tweet.entities or {}).get('hashtags', [])])
            
            csv_writer.writerow([
                tweet.id,
                tweet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                tweet.text.replace('\n', ' ').replace('\r', ' '),
                user.username,
                user.public_metrics['followers_count'],
                tweet.public_metrics['retweet_count'],
                tweet.public_metrics['like_count'],
                tweet.lang,
                hashtags,
                user.verified
            ])

    print(f"Successfully saved {len(tweets)} tweets to {csv_file_path}")

except Exception as e:
    print(f"Error: {e}")