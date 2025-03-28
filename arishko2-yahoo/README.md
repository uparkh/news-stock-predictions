# Summary

## Jupyter Notebook
* In the notebook, I scraped Yahoo Finance to grab the date, title, and article content using BeautifulSoup4
* I used a googlesearch api to grab the links and wrote them to a json file which my python script read to scrape the data
* I requested 1000 links but had a lot of duplicates so I used a set to get rid of duplicates, perhaps would have been easier to remove duplicates before writing them to a file

## Python script

* `python3 scraper.py --help` will give you all the args u need to run it
* We will probably grab the data off yahoo finance. Its trivial to download the csv

## Next steps...
* next steps are running the articles through a model.

