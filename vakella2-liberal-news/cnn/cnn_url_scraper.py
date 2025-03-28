import json
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def get_google_news_links(query, start_date="2024-01-01", end_date="2024-12-31", max_results=10, file_name="output.json"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    search_query = f"site:cnn.com/markets {query} after:{start_date} before:{end_date}"
    search_url = f"https://www.google.com/search?q={search_query}&num={max_results}"

    logger.info(f"Searching Google for: {search_query}")

    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve Google search results. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    article_links = []
    for item in soup.find_all('a'):
        link = item.get('href')
        if link and link.startswith('http'):
            article_links.append(link)

    article_links = article_links[:max_results]

    data = {
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "links": article_links
    }

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
        logger.info(f"Data written to {file_name}")

    return article_links

google_news_links = get_google_news_links("stock markets", max_results=50, file_name="2024_economy_links.json")
