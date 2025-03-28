import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import pandas as pd
from fake_useragent import UserAgent

URL_FILE = 'vox_article_urls.txt'
OUTPUT_FILE = 'scraped_articles.csv'

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

# def get_article_details(url):
#     try:
#         response = requests.get(url, headers=get_headers(), timeout=10)
#         if response.status_code != 200:
#             print(f"Skipping {url} (status {response.status_code})")
#             return None

#         soup = BeautifulSoup(response.text, "html.parser")

#         title = soup.find('h1', {'class': 'c-entry-title'}).get_text(strip=True)
#         date = soup.find('time', {'class': 'c-byline__item'}).get_text(strip=True)

#         paragraphs = soup.find_all('p', {'class': 'c-entry-content__paragraph'})
#         article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        
#         return {
#                 'title': title,
#                 'date': date,
#                 'text': article_text
#             }
    
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None
    
# def scrape_articles():
#     with open(URL_FILE, 'r') as f:
#         urls = f.readlines()

#     with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
#         fieldnames = ['title', 'date', 'text']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         writer.writeheader()  # Write the header row

#         for url in urls:
#             url = url.strip()
#             print(f"Scraping article: {url}")

#             article_details = get_article_details(url)
#             if article_details:
#                 writer.writerow(article_details)

#             time_delay = random.uniform(1, 4)
#             print(f"Sleeping for {time_delay:.2f} seconds before scraping next article...")
#             time.sleep(time_delay)

#     print(f"Finished scraping articles. Results saved to {OUTPUT_FILE}")

# if __name__ == "__main__":
#     scrape_articles()

def return_text_if_not_none(element):
    if element:
        return element.text.strip()
    else:
        return ''
    
def parse(html):
    soup = BeautifulSoup(html, features="html.parser")
    title = return_text_if_not_none(soup.find('h1', {'class': 'headline__text'}))
    article_content = return_text_if_not_none(soup.find('div', {'class': 'article__content'}))
    return title, article_content

url = 'https://www.vox.com/2023/10/20/23924481/killers-of-the-flower-moon-reviews-analysis-dark-history'
data = requests.get(url).text
print(parse(data))


