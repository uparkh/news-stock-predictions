import requests
import json
import time
from datetime import datetime

API_KEY = 'YDEtPRpTIKfrB9uVmPGRcj7ELNpYoWKpo'  # Replace with your actual API key
BASE_URL = 'https://api.nytimes.com/svc/archive/v1'
EXISTING_FILE = 'nytimes_2024_articles.json'  # Your existing file
OUTPUT_FILE = 'nytimes_2024_articles_complete.json'  # New complete file

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
    """Extract relevant fields from articles"""
    processed = []
    for article in articles:
        processed.append({
            'title': article.get('headline', {}).get('main'),
            'date': article.get('pub_date'),
            'snippet': article.get('snippet'),
            'url': article.get('web_url'),
            'section': article.get('section_name'),
            'word_count': article.get('word_count')
        })
    return processed

def load_existing_data():
    """Load existing data from file"""
    try:
        with open(EXISTING_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: Could not load {EXISTING_FILE}, starting fresh")
        return []

def save_complete_data(data):
    """Save complete dataset to new file"""
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nComplete dataset saved to {OUTPUT_FILE}")

def scrape_nov_dec_2024():
    """Scrape November and December 2024 articles"""
    start_time = datetime.now()
    print(f"\nStarting NY Times November-December 2024 scrape at {start_time}")
    
    # Load existing data
    all_articles = load_existing_data()
    original_count = len(all_articles)
    print(f"Loaded {original_count} existing articles")
    
    # Scrape missing months
    for month in [11, 12]:  # November and December
        print(f"\nProcessing 2024-{month:02d}...")
        articles = get_monthly_articles(2024, month)
        processed = process_articles(articles)
        all_articles.extend(processed)
        print(f"Added {len(processed)} articles from 2024-{month:02d}")
        time.sleep(12)  # Longer delay to avoid rate limiting
    
    # Save complete dataset
    save_complete_data(all_articles)
    
    # Final report
    end_time = datetime.now()
    print(f"\nScrape completed at {end_time}")
    print(f"Duration: {end_time - start_time}")
    print(f"Original article count: {original_count}")
    print(f"New articles added: {len(all_articles) - original_count}")
    print(f"Total articles now: {len(all_articles)}")

if __name__ == '__main__':
    scrape_nov_dec_2024()
