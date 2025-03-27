import logging
import requests
import json
import random
from bs4 import BeautifulSoup
import time
import argparse
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def write_to_file(output_file, data):
    try:
        with open(output_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

def scrape_yahoo(url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        meta_title = soup.find('meta', attrs={'name': 'title'})
        title = meta_title.get('content', 'No title found') if meta_title else 'No title found'
        paragraphs = soup.find_all('p', class_='yf-1090901')
        article_text = '\n'.join([para.get_text() for para in paragraphs])
        time_tag = soup.find('time', class_='byline-attr-meta-time')
        article_date = time_tag['datetime'] if time_tag else 'No date found'

        logging.info("Title: %s", title)
        logging.info("Date: %s", article_date)

        data = {
            "url": url,
            "title": title,
            "date": article_date,
            "article_content": article_text
        }

        write_to_file(output_file, data)

        return title, article_date, article_text
    except requests.exceptions.RequestException as e:
        logging.error("Failed to retrieve the article. Error: %s", e)
        return None, None, None

def read_links_from_file(input_file):
    links = []
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            for link in data.get("links", []):
                if link.startswith("https://finance.yahoo.com"):
                    links.append(link)
                else:
                    logging.warning("Skipping unsupported link: %s", link)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Failed to read the file. Error: %s", e)
    return links

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Yahoo Finance articles and save them to a file.")
    parser.add_argument("--input_file", help="Path to the JSON file containing links to scrape.")
    parser.add_argument("--output_file", help="Path to the JSON file where scraped articles will be saved.")
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    if not input_file or not output_file:
        logging.error("Input file or output file is not specified. Exiting.")
        exit(1)
        
    processed_links = set()

    try:
        with open(output_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
            for article in existing_data:
                processed_links.add(article["url"])
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("No existing processed links found. Starting fresh.")

    links = read_links_from_file(input_file)
    total_links = len(links)
    article_count_by_month = defaultdict(int)
    article_count_by_month_num = [0] * 12 

    for index, link in enumerate(links, start=1):
        if link in processed_links:
            logging.info("Skipping already processed link: %s", link)
            continue

        logging.info("Processing link %d/%d: %s", index, total_links, link)
        title, article_date, article_text = scrape_yahoo(link, output_file)
        if article_date and article_date != "No date found":
            month = article_date[:7]  
            article_count_by_month[month] += 1
            month_num = int(article_date[5:7]) - 1 
            article_count_by_month_num[month_num] += 1

        wait_time = 1 + random.random() * 2 + random.random() * 0.5
        logging.info("Waiting for %.2f seconds before the next request.", wait_time)
        time.sleep(wait_time)
        processed_links.add(link)

    for month_num, count in enumerate(article_count_by_month_num, start=1):
        logging.info("Month %d: %d articles", month_num, count)


