# import requests
# import json
# import time
# from datetime import datetime

# API_KEY = 'ZpFz0PBUU06Q8FUmSRhIZSY9dhHiNU5n'  # Replace with your actual API key
# BASE_URL = 'https://api.nytimes.com/svc/archive/v1'

# def get_monthly_articles(year, month):
#     """Get all articles for a specific month using Archive API"""
#     url = f"{BASE_URL}/{year}/{month}.json"
#     params = {'api-key': API_KEY}
    
#     try:
#         print(f"\nFetching articles for {year}-{month:02d}...")
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         articles = response.json().get('response', {}).get('docs', [])
#         print(f"Found {len(articles)} articles for {year}-{month:02d}")
#         return articles
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching {year}-{month}: {e}")
#         return []

# def process_articles(articles):
#     """Extract relevant fields from articles with progress printing"""
#     processed = []
#     total = len(articles)
    
#     for i, article in enumerate(articles, 1):
#         # Extract article data
#         article_data = {
#             'title': article.get('headline', {}).get('main'),
#             'date': article.get('pub_date'),
#             'snippet': article.get('snippet'),
#             'url': article.get('web_url'),
#             'section': article.get('section_name'),
#             'word_count': article.get('word_count')
#         }
#         processed.append(article_data)
        
#         # Print processing status
#         title_short = (article_data['title'][:50] + '...') if len(article_data['title']) > 50 else article_data['title']
#         print(f"Processed article {i}/{total}: {title_short}")
        
#     return processed

# def scrape_2024_articles():
#     """Scrape all NY Times articles for 2024 with detailed logging"""
#     all_articles = []
#     start_time = datetime.now()
    
#     print("Starting NY Times 2024 article scrape...")
#     print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
#     print("="*60)
    
#     for month in range(1, 13):  # January to December
#         articles = get_monthly_articles(2024, month)
#         processed = process_articles(articles)
#         all_articles.extend(processed)
#         time.sleep(6)  # Respect rate limits
    
#     # Save results
#     filename = 'nytimes_2024_articles.json'
#     with open(filename, 'w') as f:
#         json.dump(all_articles, f, indent=2)
    
#     # Final summary
#     end_time = datetime.now()
#     duration = end_time - start_time
    
#     print("\n" + "="*60)
#     print("Scraping complete!")
#     print(f"Total articles collected: {len(all_articles)}")
#     print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
#     print(f"Total duration: {duration}")
#     print(f"Results saved to: {filename}")

# if __name__ == '__main__':
#     scrape_2024_articles()

import requests
import json
import time
from datetime import datetime

API_KEY = 'DEtPRpTIKfrB9uVmPGRcj7ELNpYoWKpo'  # Replace with your actual API key
BASE_URL = 'https://api.nytimes.com/svc/archive/v1'

def get_monthly_articles(year, month):
    """Get all articles for a specific month using Archive API"""
    url = f"{BASE_URL}/{year}/{month}.json"
    params = {'api-key': API_KEY}
    
    try:
        print(f"\nFetching articles for {year}-{month:02d}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json().get('response', {}).get('docs', [])
        print(f"Found {len(articles)} articles for {year}-{month:02d}")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {year}-{month}: {e}")
        return []

def process_articles(articles):
    """Extract relevant fields from articles with progress printing"""
    processed = []
    total = len(articles)
    
    for i, article in enumerate(articles, 1):
        # Extract article data
        article_data = {
            'title': article.get('headline', {}).get('main'),
            'date': article.get('pub_date'),
            'snippet': article.get('snippet'),
            'url': article.get('web_url'),
            'section': article.get('section_name'),
            'word_count': article.get('word_count')
        }
        processed.append(article_data)
        
        # Print processing status
        title_short = (article_data['title'][:50] + '...') if len(article_data['title']) > 50 else article_data['title']
        print(f"Processed article {i}/{total}: {title_short}")
        
    return processed

def scrape_nov_dec_2024():
    """Scrape only November and December 2024 NY Times articles"""
    all_articles = []
    start_time = datetime.now()
    
    print("Starting NY Times November-December 2024 article scrape...")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Only process November (11) and December (12)
    for month in [11, 12]:
        articles = get_monthly_articles(2024, month)
        processed = process_articles(articles)
        all_articles.extend(processed)
        time.sleep(12)  # Increased delay to avoid rate limiting
    
    # Save results
    filename = 'nytimes_nov_dec_2024_articles.json'
    with open(filename, 'w') as f:
        json.dump(all_articles, f, indent=2)
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("Scraping complete!")
    print(f"Total articles collected: {len(all_articles)}")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration}")
    print(f"Results saved to: {filename}")

if __name__ == '__main__':
    scrape_nov_dec_2024()
