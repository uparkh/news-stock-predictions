import pandas as pd
import nltk
import re
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

english_stopwords = set(stopwords.words('english'))
nltk.download('all')

df = pd.concat([
    pd.read_csv('reddit-cryptocurrency-data.csv'),
    pd.read_csv('reddit-wallstreetbets-data.csv'),
    pd.read_csv('reddit-finance-data.csv'),
    pd.read_csv('reddit-investing-data.csv'),
], ignore_index=True)


# Combine `post_title`, `post_selftext` into a column 'headline'
cols_to_combine = ['post_title', 'post_selftext']
df['headline'] = df[cols_to_combine].fillna('').agg(' '.join, axis=1)
df = df.drop(columns=cols_to_combine)


# ## Text Cleaning Function
# I did research the tradeoff between stemming vs. lemmatizing, and in general I got that:
# - Stemming = rules-based, heuristic algorithmic removal of common word endings
#     - faster for larger datasets, loses accuracy and context, can produced nonexistent words
# - Lemmatizing = more accurate, more computationally expensive with Part-of-Speech Tagging required
# 
# But I reason that I'm not training an ML model where accuracy is mission critical, so simply
# stemming should suffice.

def clean_text_stemmer(text: str) -> str:
    """
    Clean the input text by removing URLs, special characters, and extra whitespace, and using
    NLTK's tokenization, stopword removal, stemming.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove special characters and digits, keep important punctuation
    text = re.sub(r'[^A-Za-z\s.,!?]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()

    words = word_tokenize(text)
    # Remove stopwords
    words = [word for word in words if word not in english_stopwords]
    # Stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    text = ' '.join(words)
    return text + '.'

# example_text = df['text'].iloc[2226]
# example_text

example_text_stemmed = clean_text_stemmer(example_text)
example_text_stemmed

# Okay, maybe lemmatizing is the better strategy, there are just too many nonsense words here that can throw off the sentiment analyzer.

def clean_text_lemmatizer(text: str) -> str:
    """
    Clean the input text by removing URLs, special characters, and extra whitespace, and using
    NLTK's tokenization, stopword removal, lemmatizer.
    """
    # POS tagging for lemmatization
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    pos_tags = pos_tag(word_tokenize(text))
    lemmatizer = WordNetLemmatizer()
    # Map POS tags to WordNet format
    tag_dict = {
        "J": wordnet.ADJ,  # Adjective
        "N": wordnet.NOUN, # Noun
        "V": wordnet.VERB, # Verb
        "R": wordnet.ADV   # Adverb
    }
    pos_tags = [(word, tag_dict.get(tag[0], 'n')) for word, tag in pos_tags]

    # Lemmatization
    words = [lemmatizer.lemmatize(word, pos).lower() for word, pos in pos_tags]
    # Remove stopwords
    words = [word for word in words if word not in english_stopwords]
    text = ' '.join(words)

    # Remove special characters and digits, keep important punctuation
    text = re.sub(r'[^A-Za-z\s.,!?]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()

    return text + '.'  # For FinBERT

example_text

example_text_lemmatized = clean_text_lemmatizer(example_text)
print('LEMMATIZED: ' + example_text_lemmatized)
print('STEMMED: ' + example_text_stemmed)

# ## Applying Lemmatizer to Whole Text Column
# Okay the lemmatizer **definitely works a lot better**, it's a whole lot more accurate in its processing. Gonna stick with that! Now to apply it to the whole text column.

# For some reason there are floats in the text data, have to replace those with empty string
cols = ['headline'] + [f'tc{i}' for i in range(10)]
df[cols] = df[cols].astype(str)

for col in cols:
    df[col] = df[col].apply(clean_text_lemmatizer)

df.sample(4)

# Save the cleaned DataFrame to a new CSV file
df.to_csv('reddit-cleaned.csv', index=False)


import pandas as pd

# # Sentiment Models Comparisons -- Reddit
# In this part (3), I'll be comparing the VADER pretrained model from NLTK's presets, and the FinBERT model from the PyTorch library.
# 
# The idea is that using a sentiment analysis model trained on financial data will allow it to pick up financial terms and keywords from the corpora better than the general purpose NLTK pretrained sentiment model.
# 
# I'm not sure exactly yet how I'll measure this effect, but for each model's results, I'll make a plot of sentiment results for each month of 2024. Then I'll decide from there.
# 
# ## Data Treatment
# The cleaned data consists of lemmatized top comments, and the "headline" column which has the post title + self text
# 
# Here's what I'll do. For each post:
# - Get a sentiment score for the post title + self text (headline), call it $s_0$
# - Get a sentiment score for each top comment, call them $s_1, s_2, ..., s_{10}$
# - Get a weighted aggregate sentiment score for the post. Weighing a score $s_i$ less as $i$ increases. I will just begin with the simple function: $w(s_i) = \frac{1}{100} * (i - 10)^2 + 0.01$ to multiply to a score to weigh it. The $0.01$ is to just avoid weighing the last element at 0.
# 
# For each month, I will take the median score of the post scores of that month as the representation for the entire month, as this statistic is more resistant to outliers.
# 
# I have to do it like this because sentiment analysis really starts to break when the text gets too long, either with NLTK's VADER, or with FinBERT. You will see this in my previous commits if you want to look, but essentially I tried to combine all the info associated with each post into one supertext of the post, and tried to run an analysis ont that, but the models failed spectacularly with incredibly large bodies of text like that.
# 
# 

df = pd.read_csv('reddit-cleaned.csv')

df.sample(3)

df.drop(columns=['post_id'], inplace=True)

df.sample(3)

subreddits = df['subreddit'].unique()
print(subreddits)

months = df['month'].unique()
print(months)

# Average character length of the text in the combined dataframe
cols = ['headline'] + [f'tc{i}' for i in range(10)]
for col in cols:
    avg_length = df[col].str.len().mean()
    print(f"Average character length of '{col}': {avg_length}")

# Some columns are not of the correct data type
df[cols] = df[cols].astype(str)

# Okay these are all reasonable character lengths, so I think the sentiment analyses should be much nicer compared to my previous attempt.

# ## NLTK Sentiment Analysis
# In this section I'll use NLTK's sentiment analysis to convert all the columns into sentiment scores.

sample_headline = df['headline'].sample(1).values[0]
print(sample_headline)

from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

sia.polarity_scores(sample_headline)

# ### Compound Scores
# So this mechanism divides it's output into a negative, neutral, positive, and compound score.
# I'll just use compound for now, and see what the scores are.

# Apply the sentiment analysis and create new columns for each score
for col in cols:
    df[f'nltk_{col}'] = df[col].apply(lambda x: pd.Series(sia.polarity_scores(x)['compound']))

nltk_cols = ['nltk_' + col for col in cols]
df[nltk_cols].describe()

# Okay so it seems that a majority of scores are slightly positive. But this is across the columns. Perhaps after I run my special weighted mean on each post and then take the median grouped by month, I'll see a different story.

def weighted_mean(row: pd.Series, cols: list[str]) -> float:
    def w(i: int) -> float:
        return 2.718281828459045 ** (-3 * i / len(cols))

    return sum([row[col] * w(i) for i, col in enumerate(cols)])

df['nltk_mu'] = df.apply(lambda row: weighted_mean(row, nltk_cols), axis=1)
nltk_month_avg = df.groupby('month', sort=False)['nltk_mu'].mean()

nltk_month_avg

# Hmm, still all positive! Note that this isn't a horrible thing, I shouldn't shape the results to my expectation. Looking at the actual S&P 500 graph:
# ![S&P 500 Graph 2024](S&P_500_2024.png)
# 
# Can see that there was a dip in March and July/August of that year, which does correspond to dips in sentiment scores around that time in the data, despite being positive, so perhaps there's something there! Let's standardize to see in detail.

nltk_month_avgs_standardized = (nltk_month_avg - nltk_month_avg.mean()) / nltk_month_avg.std()
nltk_month_avgs_standardized

# Honestly pretty good! If we think out a monthly score of 0 representing a neutral attitude, a negative score seems to correlate to a bearish outlook versus a positive score being a bullish outlook in the short term.

# ## FinBERT Sentiment Analysis
# Let's see how FinBERT does, given that it is specially trained on financial texts and sources.

from transformers import pipeline

finance_sentiment = pipeline("text-classification", model="ProsusAI/finbert")

finance_sentiment([sample_headline, sample_headline])

from nltk import word_tokenize
from tqdm import tqdm

# Trim length of all entries to 256 tokens
# BERT tokens are defined differently to NLTK tokens, so I ran into issues with only accepting
# 512 tokens. I decided to use 256 tokens instead to avoid this issue.
def trim(text: str) -> str:
    tokens = word_tokenize(text)
    text = ' '.join(tokens[:256])
    return text

for col in tqdm(cols):
    df[col] = df[col].apply(trim)

# Batch processing because we are interfacing with an ML model, faster than processing one by one
for col in tqdm(cols):
    df[f'finbert_{col}'] = [result['score'] for result in finance_sentiment(df[col].tolist())]

finbert_cols = ['finbert_' + col for col in cols]
df[finbert_cols].describe()

df['finbert_mu'] = df.apply(lambda row: weighted_mean(row, finbert_cols), axis=1)
fb_month_avg = df.groupby(['month', 'subreddit'], sort=False)['finbert_mu'].mean().unstack()

fb_month_avg

# It seems that all the scores still are quite high, but the subtle patterns are there that correlate to March and July/August dips. Maybe standardizing could be helpful to see the dips.

fb_month_avgs_standardized = (fb_month_avg - fb_month_avg.mean(axis=0)) / fb_month_avg.std(axis=0)

pd.concat([nltk_month_avgs_standardized, fb_month_avgs_standardized], axis=1, keys=['nltk', 'finbert'])

# ![S&P500 2024 Graph](S&P_500_2024.png)
# Little better, it seems that FinBERT follows similar trends to NLTK, but FinBERT's June is way too pessimistic, and FinBERT's July is way too optimistic. Based on the actual S&P500 graph, it seems that NLTK actually performed better, so I will be using NLTK for my plotting and analysis moving forward.

df.to_csv('reddit-sentiment.csv', index=False)




import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import textwrap


idf = pd.read_csv('./reddit-sentiment.csv')  # input df
sdf = pd.read_csv('../arishko2-yahoo/data/HistoricalData_1743103651771.csv')  # yahoo S&P500 data

# Convert 'Date' column to datetime format
sdf['Date'] = pd.to_datetime(sdf['Date'])
sdf_2024 = sdf[sdf['Date'].dt.year == 2024]
sdf_2024 = sdf_2024.sort_values(by=['Date'])
sdf_2024 = sdf_2024.reset_index(drop=True)

sdf_2024 = sdf_2024[['Date', 'Close/Last']]
sdf_2024

start_price = sdf_2024.iloc[0]['Close/Last']
end_price = sdf_2024.iloc[-1]['Close/Last']
baseline_slope = (start_price - end_price) / len(sdf_2024)

sdf_2024['Baseline'] = start_price - (baseline_slope * sdf_2024.index)
sdf_2024['Deviation'] = sdf_2024['Close/Last'] - sdf_2024['Baseline']

# convert month names to datetime objects
def month_to_datetime(month):
    return datetime.strptime(f"2024-{month}-01", "%Y-%b-%d")

mo_idf = idf.groupby('month', sort=False)['nltk_mu'].mean()
mo_idf_standardized = (mo_idf - mo_idf.mean()) / mo_idf.std()
mo_idf_standardized.index = mo_idf_standardized.index.map(month_to_datetime)

plt.figure(figsize=(12, 6))
# plt.plot(sdf_2024['Date'], sdf_2024['Close/Last'], linestyle=':', color='b', label='Close/Last')
# plt.plot(sdf_2024['Date'], sdf_2024['Baseline'], linestyle='--', color='orange', label='Baseline')
plt.plot(sdf_2024['Date'], sdf_2024['Deviation'], linestyle='-', color='purple', label='Deviation')
mag = sdf_2024['Deviation'].max()
mag += mag / 12

colors = ['green' if val > 0 else 'red' for val in mo_idf_standardized]
widths = [delta.days for delta in (mo_idf_standardized.index[1:] - mo_idf_standardized.index[:-1])] + [31]
plt.bar(mo_idf_standardized.index, mo_idf_standardized * (mag / 3), color=colors, width=widths, align='edge')

plt.title('2024 S&P 500: Adjusted Relative to Trendline')
plt.xlabel('Date')
plt.ylabel('Price Deviation from Trendline ($)')
plt.grid(True)
plt.xticks(rotation=45)

plt.ylim(-mag, mag)

plt.xlim(sdf_2024['Date'].iloc[0], sdf_2024['Date'].iloc[-1])
plt.tight_layout()
plt.show()




