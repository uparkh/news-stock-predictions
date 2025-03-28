import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from fake_useragent import UserAgent

BASE_URL = 'https://www.vox.com'
ARCHIVE_URLS = [
    'https://www.vox.com/archives/2024/1/1', 'https://www.vox.com/archives/2024/10/1', 
    'https://www.vox.com/archives/2024/11/1', 'https://www.vox.com/archives/2024/12/1',
    'https://www.vox.com/archives/2024/12/10', 'https://www.vox.com/archives/2024/12/11',
    'https://www.vox.com/archives/2024/12/2', 'https://www.vox.com/archives/2024/12/3',
    'https://www.vox.com/archives/2024/12/4', 'https://www.vox.com/archives/2024/12/5',
    'https://www.vox.com/archives/2024/12/6', 'https://www.vox.com/archives/2024/12/7',
    'https://www.vox.com/archives/2024/12/8', 'https://www.vox.com/archives/2024/12/9',
    'https://www.vox.com/archives/2024/2/1', 'https://www.vox.com/archives/2024/3/1',
    'https://www.vox.com/archives/2024/4/1', 'https://www.vox.com/archives/2024/5/1',
    'https://www.vox.com/archives/2024/6/1', 'https://www.vox.com/archives/2024/7/1',
    'https://www.vox.com/archives/2024/8/1', 'https://www.vox.com/archives/2024/9/1'
]

URL_FILE = 'vox_article_urls.txt'

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

def get_article_urls_from_archive(archive_url):
    all_urls = set()

    def scrape_page(url):
        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            if response.status_code != 200:
                print(f"Skipping {url} (status {response.status_code})")
                return

            soup = BeautifulSoup(response.text, "html.parser")
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/'):
                    href = BASE_URL + href

                if "vox.com" in href:
                    all_urls.add(href)

            next_button = soup.find('a', {'rel': 'next'})
            if next_button and next_button['href']:
                next_page_url = BASE_URL + next_button['href']
                print(f"Found next page: {next_page_url}")
                scrape_page(next_page_url)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Scraping archive: {archive_url}")
    scrape_page(archive_url)

    return all_urls

def scrape_all_archives():
    all_article_urls = set()

    for archive_url in ARCHIVE_URLS:
        article_urls = get_article_urls_from_archive(archive_url)
        all_article_urls.update(article_urls)

        time_delay = random.uniform(2, 5)
        print(f"Sleeping for {time_delay:.2f} seconds before scraping next archive...")
        time.sleep(time_delay)

    with open(URL_FILE, 'w') as f:
        for url in sorted(all_article_urls):
            f.write(url + '\n')

    print(f"Saved {len(all_article_urls)} article URLs to {URL_FILE}")

if __name__ == "__main__":
    scrape_all_archives()


# def get_article_urls():
#     all_urls = set()
#     data = requests.get(BASE_URL).text
#     soup = BeautifulSoup(data, features="html.parser")
    
#     for a in soup.find_all('a', href=True):
#         if a['href'] and a['href'][0] == '/' and a['href'] != '#':
#             a['href'] = BASE_URL + a['href']
#         all_urls.append(a['href'])
    
#     def url_is_article(url, current_year='2024'):
#         return url and f'cnn.com/{current_year}/' in url and '/gallery/' not in url
    
#     article_urls = [url for url in all_urls if url_is_article(url)]
    
#     with open(URL_FILE, 'w') as f:
#         for url in article_urls:
#             f.write(url + '\n')

#     print(f"Saved {len(article_urls)} article URLs to {URL_FILE}")


# def load_article_urls():
#     if not os.path.exists(URL_FILE):
#         print(f"{URL_FILE} not found. Run get_article_urls() first.")
#         return []
    
#     with open(URL_FILE, 'r') as f:
#         return [line.strip() for line in f.readlines()]

# def return_text_if_not_none(element):
#     return element.text.strip() if element else ''

# def parse_article(html):
#     soup = BeautifulSoup(html, features="html.parser")
#     title = return_text_if_not_none(soup.find('h1', {'class': 'headline__text'}))
#     article_content = return_text_if_not_none(soup.find('div', {'class': 'article__content'}))
#     return title, article_content

# def scrape_and_save_articles(article_urls):
#     for url in article_urls:
#         try:
#             response = requests.get(url)
#             if response.status_code == 200:
#                 title, content = parse_article(response.text)
                
#                 if title and content:
#                     df = pd.DataFrame([[title, content]], columns=['Title', 'Content'])
#                     df.to_csv(CSV_FILE, mode='a', header=not pd.io.common.file_exists(CSV_FILE), index=False)
#                     print(f"Saved: {title}")
#                 else:
#                     print(f"Skipping (no content): {url}")
#             else:
#                 print(f"Failed to fetch: {url}")
#         except Exception as e:
#             print(f"Error fetching {url}: {e}")
        
#         sleep_time = random.uniform(5, 15)  # Random delay between 5-15 seconds
#         print(f"Sleeping for {sleep_time:.2f} seconds...")
#         time.sleep(sleep_time)

# if __name__ == "__main__":
#     article_urls = get_article_urls()[:5]
#     print(article_urls)
#     # scrape_and_save_articles(article_urls)


    



