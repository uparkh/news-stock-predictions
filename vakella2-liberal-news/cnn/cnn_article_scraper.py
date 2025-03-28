import requests
from bs4 import BeautifulSoup
import pandas as pd

# url = 'https://www.cnn.com/2023/07/01/politics/supreme-court-term-takeaways/index.html'
# data = requests.get(url).text

def return_text_if_not_none(element):
    if element:
        return element.text.strip()
    else:
        return ''

def parse(html):
    soup = BeautifulSoup(html, features="html.parser")
    title = return_text_if_not_none(soup.find('h1', {'class': 'headline__text'}))
    article_content = return_text_if_not_none(soup.find('div', {'class': 'article__content'}))
    timestamp = return_text_if_not_none(soup.find('div', {'class': 'timestamp'}))
    return title, article_content, timestamp

with open('cnn_business_links_clean.txt', 'r') as file:
    urls = [line.strip() for line in file.readlines()]

with open("cnn_business_articles.csv", "w", newline="", encoding="utf-8") as file:
    df = pd.DataFrame(columns=["Title", "Content", "Timestamp"])
    df.to_csv(file, index=False)

for url in urls:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
        title, content, timestamp = parse(response.text)
        with open("cnn_business_articles.csv", "a", newline="", encoding="utf-8") as file:
            df = pd.DataFrame([[title, content, timestamp]], columns=["Title", "Content", "Timestamp"])
            df.to_csv(file, header=False, index=False)
        print(f"Saved: {url}")
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
