import twint
import pandas as pd
import csv  # Added missing import
from datetime import datetime, timedelta
import nest_asyncio  # Needed for Jupyter/twint compatibility

# Apply nest_asyncio fix
nest_asyncio.apply()

def fetch_tweets_2024():
    """Fetches tweets for each month in 2024 using Twint."""
    monthly_tweets = {}
    query = "finance OR stock OR market OR investing lang:en -is:retweet"

    for month in range(1, 13):  # Jan-Dec 2024
        month_name = datetime(2024, month, 1).strftime('%b')  # "Jan", "Feb", etc.
        start_date = datetime(2024, month, 1).strftime('%Y-%m-%d')
        end_date = datetime(2024, month + 1, 1).strftime('%Y-%m-%d') if month < 12 else datetime(2025, 1, 1).strftime('%Y-%m-%d')

        print(f"Fetching tweets for {month_name} 2024...")

        # Configure Twint
        c = twint.Config()
        c.Search = query
        c.Since = start_date
        c.Until = end_date
        c.Limit = 100
        c.Pandas = True
        c.Hide_output = True
        c.Store_object = True

        try:
            twint.run.Search(c)
            tweets_df = twint.storage.panda.Tweets_df
            if not tweets_df.empty:
                monthly_tweets[month_name] = tweets_df['tweet'].tolist()[:100]  # Ensure max 100 tweets
            else:
                print(f"No tweets found for {month_name}.")
        except Exception as e:
            print(f"Error fetching {month_name}: {str(e)}")
            continue  # Continue to next month if error occurs

    return monthly_tweets

def save_to_csv(monthly_tweets, filename="2024_tweets_twint.csv"):
    """Saves tweets in CSV format: [month, text0]."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['month', 'text0'])
        
        for month, texts in monthly_tweets.items():
            for text in texts:
                writer.writerow([month, text.replace('\n', ' ').replace('\r', ' ')])

if __name__ == "__main__":
    monthly_tweets = fetch_tweets_2024()
    if monthly_tweets:  # Only save if we got data
        save_to_csv(monthly_tweets)
        print(f"CSV saved successfully with {sum(len(v) for v in monthly_tweets.values())} tweets!")
    else:
        print("No tweets were fetched.")